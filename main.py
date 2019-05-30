from flask import Flask, render_template, request, url_for, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
import markdown, random, string


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(100000), unique=False, nullable=False)
    url = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return "<Posts %r>" % self.url


def randomUrl():

    letters = string.ascii_letters + string.digits

    url = "".join(random.choice(letters) for i in range(4))

    return url


@app.route("/", methods=["GET", "POST"])
def index():

    url = ""
    err = ""

    if request.method == "POST":

        text = markdown.markdown(request.form["article"])
        slug = request.form["slug"]

        if text != "":

            if slug != "":

                url = slug

            else:

                slug = randomUrl()

                url = slug

            # insert post to database
            newPost = Posts(post=text, url=url)
            db.session.add(newPost)
            db.session.commit()

        else:

            err = "Veuillez écrire un markdown"

    return render_template("home.html", url=url, err=err)


@app.route("/articles/<slug>")
def articles(slug):

    post = Posts.query.filter_by(url=slug).first()

    return render_template("articles.html", post=post)


@app.route("/admin/")
def admin():
    auth = request.authorization
    if auth and auth.username == "username" and auth.password == "pass":

        posts = Posts.query.all()

        return render_template("admin.html", height=len(posts), posts=posts)

    return make_response(
        "Désolé, authentification impossible",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


@app.route("/admin/update/<id>", methods=["POST", "GET"])
def update(id):

    err = ""
    post = Posts.query.filter_by(id=id).first()

    if request.method == "POST":

        text = markdown.markdown(request.form["content"])

        if text != "":

            post.post = text
            db.session.commit()

            return redirect(url_for("admin"))

        else:

            err = "Veuillez écrire un markdown"

    return render_template("update.html", post=post, err=err)


@app.route("/admin/delete/<id>")
def delete(id):
    post = Posts.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("admin"))
