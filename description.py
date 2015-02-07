from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import spacy.en
from spacy.parts_of_speech import ADJ, NOUN, VERB
from gensim import corpora, models, similarities

from schema import Review, Course, Professor
from run import app

nlp = spacy.en.English()
pool = ThreadPool(3)

common = {"he", "him", "his", "her", "she", "i", "you", "", "is", "were",
          "was", "'s", "are", "had", "have", "do", "be", "will", "they", 
          "my", "can", "would", "could", "does", "your", "we", "it", "us",
          "did", "'ll", "go", "its"}

def tokenize(s):
    if s:
        return [token.string.strip()
                for token in nlp(s.lower(), parse=False, tag=True)
                if token.pos in {ADJ, NOUN, VERB} and token.string.strip() not in common]
    else:
        return []

def courses():
    with app.app_context():
        data = [course.description for course in Course.query.order_by(Course.id).all()]

    courses = pool.map(tokenize, data)

    d = corpora.Dictionary(courses)
    d.save("gensim/courses.dict")

    corpus = pool.map(d.doc2bow, courses)
    corpora.MmCorpus.serialize("gensim/courses.mm", corpus)

    corpus = corpora.MmCorpus("gensim/courses.mm")

    tfidf = models.TfidfModel(corpus)
    tfidf.save("gensim/courses.tfidf")
    corpus = tfidf[corpus]

    model = models.LsiModel(corpus, id2word=d, num_topics=64)
    model.save("gensim/courses.lsi")
    sims = similarities.MatrixSimilarity(model[corpus])

    sims.save("gensim/courses.sim")

# courses()
# --------------------- Prep work done  -------------------------------
d = corpora.Dictionary.load("gensim/courses.dict")
tfidf = models.TfidfModel.load("gensim/courses.tfidf")
model = models.LsiModel.load("gensim/courses.lsi")
#model = models.LdaMulticore.load("gensim/reviews.lda")

sims = similarities.MatrixSimilarity.load("gensim/courses.sim")

with app.app_context():
    course_ids = [c.id for c in Course.query.order_by(Course.id).all()]
    course_ids = np.array(course_ids)

def course_recommend(cids, pids, num=5):
    c1, c2 = [], []
    with app.app_context():
        if cids:
            c1 = Course.query.filter(Course.id.in_(cids)).all()
        if pids:
            c2 = Course.query.join(Course.reviews).join(Review.professors).filter(Professor.id.in_(pids)).all()

    courses = {c.description for c in c1 if c.description} | {c.description for c in c2 if c.description}
    if not courses:
        return {}

    vectors = model[tfidf[[d.doc2bow(tokenize(course)) for course in courses]]]
    ss = sum(sims[vectors]) / len(vectors)

    scores = {}
    for i, cid in enumerate(ss):
        scores[course_ids[i]] = cid

    return scores 

if __name__ == "__main__":
    print "\n\n".join([r.name for r in course_recommend([1908], [1891, 119])])
