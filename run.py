from flask import Flask, render_template, request
from schema import Professor, Course, Review, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///culpa.db"
db.init_app(app)

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/search/", methods=["POST"])
def search():
    return request.form["search"]

if __name__ == "__main__":
    app.run(debug=True)


