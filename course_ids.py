from __future__ import print_function

import json
from urlparse import urljoin

import requests
import frequests
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker, load_only

from schema import engine, Professor, Review, Course

Session = sessionmaker(bind=engine)
session = Session()


r = requests.get("http://culpa.info/")
soup = BeautifulSoup(r.text)
hrefs = {link["href"].split("/")[-1]
         for link in soup.find(class_="department-list").find_all("a")
         if "department" in link["href"]}
hrefs.remove("CORE")
hrefs.add("108")


course_ids = {course.id 
              for course in session.query(Course).options(load_only("id")).all()}
"""
ids = {course.id for course in session.query(Course).all()}

for href in hrefs:
    r = requests.get("http://api.culpa.info/courses/department_id/" + href)
    data = json.loads(r.text)
    for course in data["courses"]:
        c = Course(id=course["id"], name=course["name"], number=course["number"])
        if course["id"] not in course_ids:
            session.add(c)
            course_ids.add(course["id"])
session.commit()
"""

rids = {review.id for review in session.query(Review).all()}
for i, cid in enumerate(course_ids):
    if any(course.reviews
           for course in session.query(Course).filter(Course.id == cid).all()):
        continue

    try:
        r = requests.get("http://api.culpa.info/reviews/course_id/" + str(cid))

        data = json.loads(r.text)
        for review in data["reviews"]:
            if not review or review["id"] in rids:
                continue

            rids.add(review['id'])

            r = Review(id=review["id"], review=review["review_text"], workload=review["workload_text"], course_id=cid)

            pids = review["professor_ids"]
            for pid in pids:
                if not session.query(Professor).filter(Professor.id == pid).all():
                    p = requests.get("http://api.culpa.info/professors/professor_id/" + str(pid))

                    try:
                        pdata = json.loads(p.text)["professors"][0]
                    except IndexError:
                        continue

                    if pdata["nugget"] == "None":
                        pdata["nugget"] = 0
                    elif pdata["nugget"] == "Silver":
                        pdata["nugget"] = 1
                    elif pdata["nugget"] == "Gold":
                        pdata["nugget"] = 2

                    session.add(Professor(**pdata))

                prof = session.query(Professor).filter(Professor.id == pid).first()
                r.professors.append(prof)
                session.add(r)

            session.commit()
    except KeyboardInterrupt:
        raise
    except:
        print(cid)
