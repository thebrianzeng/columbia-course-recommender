from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table("association",
        db.Column("professor_id", db.Integer, db.ForeignKey("professor.id")),
        db.Column("review_id", db.Integer, db.ForeignKey("review.id")))

class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    number = db.Column(db.String)
    reviews = db.relationship("Review", backref="course")

class Professor(db.Model):
    __tablename__ = "professor"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    middle_name = db.Column(db.String)
    nugget = db.Column(db.Integer)

    reviews = db.relationship("Review",
                           secondary=association_table,
                           backref="professors")

class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String)
    workload = db.Column(db.String)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))


if __name__ == "__main__":
    db.create_all()
