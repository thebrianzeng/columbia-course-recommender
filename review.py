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
    return [token.string.strip()
            for token in nlp(s.lower(), parse=False, tag=True)
            if token.pos in {ADJ, NOUN, VERB} and token.string.strip() not in common]

def reviews():
    with app.app_context():
        data = [review.review for review in Review.query.order_by(Review.id).all()]

    reviews = pool.map(tokenize, data)

    d = corpora.Dictionary(reviews)
    d.save("gensim/reviews.dict")

    corpus = pool.map(d.doc2bow, reviews)
    corpora.MmCorpus.serialize("gensim/reviews.mm", corpus)

    corpus = corpora.MmCorpus("gensim/reviews.mm")

    tfidf = models.TfidfModel(corpus)
    tfidf.save("gensim/reviews.tfidf")
    corpus = tfidf[corpus]

    model = models.LsiModel(corpus, id2word=d, num_topics=256)
    model.save("gensim/reviews.lsi")
    sims = similarities.MatrixSimilarity(model[corpus])

    sims.save("gensim/reviews.sim")

#reviews()
# --------------------- Prep work done  -------------------------------
d = corpora.Dictionary.load("gensim/reviews.dict")
tfidf = models.TfidfModel.load("gensim/reviews.tfidf")
model = models.LsiModel.load("gensim/reviews.lsi")
#model = models.LdaMulticore.load("gensim/reviews.lda")

sims = similarities.MatrixSimilarity.load("gensim/reviews.sim")

courses = {}
with app.app_context():
    for i, review in enumerate(Review.query.order_by(Review.id).all()):
        if review.course_id not in courses:
            courses[review.course_id] = []
        courses[review.course_id].append(i)

with app.app_context():
    rids = [r.id for r in Review.query.order_by(Review.id).all()]
    rids = np.array(rids)   # allow fancy indexing

def review_recommend(cids, pids, num=5):
    r1, r2 = [], []
    with app.app_context():
        if cids:
            r1 = Review.query.join(Review.course).filter(Course.id.in_(cids)).all()
        if pids:
            r2 = Review.query.join(Review.professors).filter(Professor.id.in_(pids)).all()

    reviews = {r.review for r in r1} | {r.review for r in r2}
    if not reviews:
        return {}

    vectors = model[tfidf[[d.doc2bow(tokenize(review)) for review in reviews]]]
    ss = sum(sims[vectors]) / len(vectors)

    s = {}
    for key in courses:
        s[key] = sum(ss[courses[key]]) / (1.5 + len(courses[key]))

    return s

if __name__ == "__main__":
    reviews()
    #print "\n\n".join([r.name for r in review_recommend([1908], [1891, 119])])
