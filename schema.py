from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///culpa.db")
Base = declarative_base()

association_table = Table("association", Base.metadata,
        Column("professor_id", Integer, ForeignKey("professor.id")),
        Column("review_id", Integer, ForeignKey("review.id")))

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    reviews = relationship("Review", backref="course")

class Professor(Base):
    __tablename__ = "professor"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    nugget = Column(Integer)

    reviews = relationship("Review",
                           secondary=association_table,
                           backref="professors")

class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True)
    review = Column(String)
    workload = Column(String)

    course_id = Column(Integer, ForeignKey("course.id"))


class ShortenedCourseReview(Base):
    __tablename__ = "course_reviews"

    id = Column(Integer, primary_key=True)
    review = Column(String)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
