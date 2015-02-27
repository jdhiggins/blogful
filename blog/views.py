from flask import render_template

from blog import app
from database import session
from models import Post

@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    #Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by
    
    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0
    
    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]
    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

from flask.ext.login import login_required

@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")

@app.route("/post/<int:post_id>/edit", methods=["GET"])
@login_required
def edit_post_get(post_id):
    post_id = post_id
    posts = session.query(Post).get(post_id)
#    posts = posts.order_by(Post.datetime.asc())
#    posts = posts[post_id:(post_id + 1)]
    title = posts.title
    fill = posts.content
    post_id = posts.id
    author = posts.author_id
    if author != current_user.id:
        flash("Must be the author of the post to edit, please logout above and log in to edit", "danger")
        return redirect(url_for("posts"))
    else:
        return render_template("edit_post.html",
            title=title,
            post_id=posts,
            fill=fill)

@app.route("/post/<int:post_id>/delete", methods=["GET"])
@login_required
def delete_post_get(post_id):
    post_id = post_id
#    posts = session.query(Post)
    posts = session.query(Post).get(post_id)
#    posts = posts.order_by(Post.datetime.asc())
#    posts = posts[post_id:(post_id + 1)]
    title = posts.title
    content = posts.content
    post_id = posts.id
    author = posts.author_id
    if author != current_user.id:
        flash("Must be the author of the post to edit, please logout above and log in to edit", "danger")
        return redirect(url_for("posts"))
    else:
        return render_template("delete_post.html",
            title=title,
            post_id=posts,
            content=content)

import mistune
from flask import request, redirect, url_for


from flask.ext.login import current_user

@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
        author=current_user
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))


@app.route("/post/<int:post_id>/edit", methods=["POST"])
def edit_post_post(post_id):
    post = session.query(Post).get(post_id) 
    post.title = request.form["title"]
    post.content = mistune.markdown(request.form["content"])
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post_post(post_id):
    post = session.query(Post).get(post_id) 
    session.delete(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:post_id>")
def single_full_post(post_id):
    post_id = post_id
    posts =[]
    single_post = session.query(Post).get(post_id)
    posts.append(single_post)
#    posts = session.query(Post)
#    posts = posts.order_by(Post.datetime.asc())
#    posts = posts[post_id:(post_id + 1)]
    return render_template("posts.html",
        posts=posts,
        has_next=None,
        has_prev=None,
        page=None,
        total_pages=None
    )

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

from flask import flash
from flask.ext.login import login_user
from werkzeug.security import check_password_hash
from .models import User
from flask.ext.login import logout_user

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    
    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))

@app.route("/logout", methods=["GET"])
#@login_required
def logout():
    logout_user()
    return redirect(url_for("posts"))

#@app.route("/logout", methods=["POST"])
#def logout_user_user():
#    logout_user()
#    return redirect(url_for("posts"))

