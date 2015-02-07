from collections import OrderedDict

from run import app, Course
import review
import description

def recommend(cids, pids, num=5):
    rev_scores = review.review_recommend(cids, pids)
    des_scores = description.course_recommend(cids, pids)

    scores = dict(rev_scores)
    for key in des_scores:
        if key in scores:
            scores[key] = (scores[key] + des_scores[key]) / 2
        else:
            scores[key] = des_scores[key]

    if scores:
        cids = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:num]
    else:
        raise Exception("No class, reviews")

    with app.app_context():
        return OrderedDict((Course.query.filter(Course.id == cid).first(), (scores[cid], rev_scores.get(cid, None), des_scores.get(cid, None)))
                            for cid in cids)

if __name__ == "__main__":
    print "\n\n".join([r.name for r in recommend([1908], [1891, 119])])
