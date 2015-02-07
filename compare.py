from collections import OrderedDict

from run import app, Course
import numpy as np
import review
import description

rweight = 1
dweight = 0.25
def recommend(cids, pids, num=5):
    rev_scores = review.review_recommend(cids, pids)
    des_scores = description.course_recommend(cids, pids)

    scores = {}
    for key in rev_scores:
        if key in des_scores:
            scores[key] = (rweight * rev_scores[key] + dweight * des_scores[key]) / (dweight + rweight)
        else:
            scores[key] = rev_scores[key]

    
    assert bool(scores)
    cids = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:num]

    with app.app_context():
        return OrderedDict((Course.query.filter(Course.id == cid).first(), scores[cid])
                            for cid in cids)

if __name__ == "__main__":
    print "\n\n".join([r.name for r in recommend([1908], [1891, 119])])
