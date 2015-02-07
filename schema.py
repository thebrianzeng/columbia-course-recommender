from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.whooshalchemy

db = SQLAlchemy()

association_table = db.Table("association",
        db.Column("professor_id", db.Integer, db.ForeignKey("professor.id")),
        db.Column("review_id", db.Integer, db.ForeignKey("review.id")))

class Course(db.Model):
    __tablename__ = "course"
    __searchable__ = ["name", "number"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    number = db.Column(db.String)
    reviews = db.relationship("Review", backref="course")

class Professor(db.Model):
    __tablename__ = "professor"
    __searchable__ = ["first_name", "last_name", "middle_name"]

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
    __searchable__ = ["review", "workload"]

    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String)
    workload = db.Column(db.String)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

class ShortenedCourseReview(Base):
    __tablename__ = "course_reviews"

    id = Column(Integer, primary_key=True)
    review = Column(String)


if __name__ == "__main__":
    db.create_all()
