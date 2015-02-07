import logging
import nltk
from sqlalchemy.orm import sessionmaker, load_only
from gensim import corpora, models, similarities

from schema import engine, Professor, Review, Course, ShortenedCourseReview

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

Session = sessionmaker(bind=engine)
session = Session()


class MyCorpus(object):

    def __init__(self, dictionary, reviews):
        self.dictionary = dictionary
        self.reviews = reviews

    def __iter__(self):
        for review in self.reviews:

            # assume there's one document per line, tokens separated by whitespace
            yield self.dictionary.doc2bow()


def get_reviews_for_class(class_id):
    reviews = session.query(Review).filter(Review.course_id == class_id).all()
    return reviews


def get_counts_for_class(class_id):
    try:
        reviews = get_reviews_for_class(class_id)
    except:
        return
    tokens = []
    for review in reviews:
        tokens.extend(nltk.word_tokenize(review.review.lower()))
        # tokens.extend(nltk.word_tokenize(review))

    tagged_text = nltk.pos_tag(tokens)
    adjs = {tagged_word[0] for tagged_word in tagged_text if tagged_word[1]
            == 'JJ'}
    counts = {item: tokens.count(item) for item in adjs if tokens.count(item)
              > 1}
    words = " ".join(key for key, count in counts.iteritems()
                     for i in xrange(count))
    # for item, count in counts.viewitems():
    #     for i in range(count):
    #         words += item + " "

    scr = ShortenedCourseReview(id=class_id, review=words)
    # print scr
    session.add(scr)
    session.commit()
    # return [words]


def create_dictionary_and_corpus():
    stoplist = set('for a of the and to in'.split())
    # documents = session.query(Review).all()
    documents = session.query(Review).filter(Review.course_id == 73).all()

    texts = [[word for word in document.review.lower().split() if word not in
              stoplist]
             for document in documents]
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if
                      all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in texts]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    dictionary.save('/tmp/reviews.dict')
    corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100)
    corpus_lsi = lsi[corpus_tfidf]
    lsi.print_topics(100)
    lsi.save('/tmp/model.lsi')
    index = similarities.MatrixSimilarity(lsi[corpus])
    doc = session.query(Review).filter(Review.course_id == 73).first().review
    print doc
    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow]
    sims = index[vec_lsi]
    print(list(enumerate(sims)))
    # return dictionary, corpus


def generate_shortened_course_reviews():
    # course_ids = {course.id
    #               for course in
    #               session.query(Course).options(load_only("id")).all()}
    # for course_id in course_ids:
    #     get_counts_for_class(course_id)
    pass


def main():
    create_dictionary_and_corpus()
    # generate_shortened_course_reviews()
    # get_counts_for_class(1908)
    # get_counts_for_class(73)
    # words = get_counts_for_class(73)
    # words = get_counts_for_class(3623)
    # create_dictionary(words)
    # get_reviews_for_class(73)

if __name__ == '__main__': main()