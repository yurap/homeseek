from datetime import datetime, timedelta
from post import Post


def _hash_text(text):
    return hash(''.join(text.split()))


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
            hashes += map(_hash_text, p.get_random_sentences())
        return set(hashes)

    def check_is_ok(self, post):
        for s in post.get_sentences():
            if len(s.split()) < 4:
                continue
            h = _hash_text(s)
            if h in self._hashes:
                return False
        return True

    def add(self, p):
        for e in map(_hash_text, p.get_random_sentences()):
            self._hashes.add(e)
