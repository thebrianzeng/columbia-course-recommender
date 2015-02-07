import nltk
from sqlalchemy.orm import sessionmaker, load_only
from gensim import corpora, models, similarities

from schema import engine, Professor, Review, Course, ShortenedCourseReview

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
        # print class_id
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


def create_dictionary(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    # corpus = dictionary.doc2bow(words[0])
    # print corpus
    # print dictionary
    dictionary.save('/tmp/reviews.dict')
    corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
    return dictionary, corpus


def generate_shortened_course_reviews():
    course_ids = {course.id
                  for course in
                  session.query(Course).options(load_only("id")).all()}
    for course_id in course_ids:
        get_counts_for_class(course_id)


def main():
    generate_shortened_course_reviews()
    # get_counts_for_class(1908)
    # get_counts_for_class(73)
    # words = get_counts_for_class(73)
    # words = get_counts_for_class(3623)
    # create_dictionary(words)
    # get_reviews_for_class(73)

if __name__ == '__main__': main()