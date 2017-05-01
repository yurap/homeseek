from datetime import datetime, timedelta
from post import Post


class DupFinder(object):
    def __init__(self, db):
        self._db = db
        self._hashes = self._create_hashes_index()

    def _create_hashes_index(self):
        time_bound = datetime.now() - timedelta(days=14)
        hashes = []

        cursor = self._db.posts.find({'created_time': {'$gt': time_bound}})
        print '{}\tloading {} posts for dup matching ...'.format(datetime.now(), cursor.count())
        for post_data in cursor:
            p = Post(post_data)
            hashes += p.get_sentence_hashes(sample=2)
        return set(hashes)

    def check_is_ok(self, post):
        for h in post.get_sentence_hashes():
            if h in self._hashes:
                return False
        return True

    def add(self, p):
        for h in p.get_sentence_hashes(sample=2):
            self._hashes.add(h)
