from collections import OrderedDict
from flask import Flask, render_template, request, redirect, jsonify
import flask.ext.whooshalchemy as whooshalchemy
from schema import Professor, Course, Review, db
import compare

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///culpa.db"
app.config["WHOOSH_BASE"] = "whoosh/"
db.init_app(app)

whooshalchemy.whoosh_index(app, Course)
whooshalchemy.whoosh_index(app, Professor)
whooshalchemy.whoosh_index(app, Review)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/class_search/", methods=["POST"])
def class_search():
    courses = Course.query.whoosh_search(request.form["search"]).limit(5).all()
    results = [course.serialize for course in courses]
    return jsonify(data=results)


@app.route("/prof_search/", methods=["POST"])
def prof_search():
    profs = Professor.query.whoosh_search(request.form["search"]).limit(5).all()
    results = [prof.serialize for prof in profs]
    return jsonify(data=results)


@app.route("/class_process/", methods=["POST"])
def class_process():
    cids, pids = [], []
    for key, value in request.form.iteritems():
        if key.startswith('course'):
            cids.append(value)
        else:
            pids.append(value)

    courses = compare.review_recommend(cids, pids)
    return render_template("class_results.html", courses=courses)

if __name__ == "__main__":
    app.run(debug=True)
