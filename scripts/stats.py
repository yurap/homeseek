from pymongo import MongoClient
from .sources.dup_finder import DupFinder
from .sources.post import Post, PostIterator
from collections import defaultdict
db = MongoClient().homeseek
c = db.posts


def count_day_stats(posts):
    day_stats = defaultdict(int)
    for p in posts:
        p = Post(p)
        # if day_stats[p.created_time] == 1:
        #     print p.text
        day_stats[p.created_time] += 1

    return day_stats


if __name__ == '__main__':
    print 'total', c.count()

    df = DupFinder([])
    counter = 0
    for p in PostIterator(c.find()):
        if not df.check_and_add(p):
            counter += 1
            print p._id, p.text
            dup = df.find_dup(p)
            print dup._id, dup.text
            exit(1)
    print 'dups', counter
    # day_stats = count_day_stats(c.find())
    # for d in sorted(day_stats.keys()):
    #     print d, day_stats[d]

