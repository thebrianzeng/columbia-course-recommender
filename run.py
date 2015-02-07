from flask import Flask, render_template, request, redirect
import flask.ext.whooshalchemy as whooshalchemy
from schema import Professor, Course, Review, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///culpa.db"
app.config["WHOOSH_BASE"] = "whoosh/"
db.init_app(app)

whooshalchemy.whoosh_index(app, Course)
whooshalchemy.whoosh_index(app, Professor)
whooshalchemy.whoosh_index(app, Review)

@app.route("/", methods=["GET", "POST"])
def index():
    cls = request.form.keys()
    return render_template("base.html")

@app.route("/class_search/", methods=["POST"])
def class_search():
    courses = Course.query.whoosh_search(request.form["search"]).limit(5).all()
    #profs = Professor.query.whoosh_search(request.form["search"]).limit(5).all()
    return render_template("results.html", courses=courses)

@app.route("/class_process/", methods=["POST"])
def class_process():
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
