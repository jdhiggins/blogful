import os
import unittest
from urlparse import urlparse

from werkzeug.security import generate_password_hash

#from flask.ext.login import current_user

#Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session

class TestViews(unittest.TestCase):
    def setUp(self):
        """Test setup"""
        self.client = app.test_client()
        
        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
        # Create an example user
        self.user = models.User(name="Alexy", email="alexy@example.com",
                               password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True

            
    def testAddPost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
                "title": "Test Post",
                "content": "Test content"
            })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)
        
        post = posts[0]
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "<p>Test content</p>\n")
        self.assertEqual(post.author, self.user)

        
    def testEditPost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
                "title": "Test Post",
                "content": "Test content"
            })
        
        response = self.client.post("/post/1/edit", data={
                "title": "New Test Post",
                "content": "New test content"
            })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)
        
        post = posts[0]
        self.assertEqual(post.title, "New Test Post")
        self.assertEqual(post.content, "<p>New test content</p>\n")
        self.assertEqual(post.author, self.user)

        
    def testDeletePost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
                "title": "Test Post",
                "content": "Test content"
            })
        
        response = self.client.post("/post/1/delete")
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 0)
        
        
    def testLogout(self):
        self.simulate_login()
        
        response = self.client.get("/logout")
        
        self.assertEqual(urlparse(response.location).path, "/")
        
    
    def tearDown(self):
        """Test teardown"""
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
if __name__ == "__main__":
    unittest.main()
    