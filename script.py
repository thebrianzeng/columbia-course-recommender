import requests
from tqdm import tqdm

from bs4 import BeautifulSoup
from run import app, db, Course, Review, Professor

with app.app_context():
    db.create_all()
    for course in tqdm(Course.query.all()):
        if course.description:
            continue
        try:
            payload = {"site":"Directory_of_Classes", "num": 1,
                       "q": "{} {}".format(course.name, course.number).lower()}
            r = requests.get("http://search.columbia.edu/search", params=payload)
            soup = BeautifulSoup(r.text)
            if soup.find('u'):
                page = soup.find('u').text
                r = requests.get(page)
                soup = BeautifulSoup(r.text)
                for tr in soup.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) == 2 and tds[0].text.strip() == "Course Description":
                        course.description = tds[1].text.strip()
                        
        except KeyboardInterrupt:
            raise
        except:
            print course.id


        if course.id % 100 == 0:
            db.session.commit()
    db.session.commit()
