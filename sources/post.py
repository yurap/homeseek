import random
from helpers import split_to_sentences
from datetime import datetime


def _hash_text(text):
    return hash(''.join(text.split()))


class Post(object):
    # todo: make sure tags&metro are sorted at store time
    def __init__(self, data):
        self._attrs = []
        for attr in data:
            self.set(attr, data[attr])

    def set(self, attr, value):
        self._attrs.append(attr)
        setattr(self, attr, value)

    def __getitem__(self, k):
        return getattr(self, k)

    def to_json(self):
        return {attr:getattr(self, attr) for attr in self._attrs}

    def get_url(self):
        if self.group_id.startswith('-'):
            return u"https://vk.com/wall{}_{}".format(self.group_id, self.post_id)
        return u"https://www.facebook.com/groups/{}/permalink/{}/".format(self.group_id, self.post_id)

    def get_random_sentences(self, min_len=4, total=3):
        sents = [s for s in self.get_sentences() if len(s.split()) >= 4]
        if len(sents) == 0:
            return []
        return random.sample(sents, min(3, len(sents)))

    def get_sentences(self):
        return split_to_sentences(self.text)

    def get_sentence_hashes(self, sample=0):
        sents = self.get_sentences()
        sents = [s for s in sents if len(s.split()) >= 5]
        if len(sents) == 0:
            sents = [self.text]

        if sample > 0:
            sents = random.sample(sents, min(sample, len(sents)))

        return map(_hash_text, sents)

    def get_checksum(self):
        return hash(''.join([w.strip() for w in self.text.lower().split()]))

    def check_is_old(self):
        d = datetime.now() - self.created_time
        return d.total_seconds() / 3600. / 24 > 14


class PostIterator(object):
    def __init__(self, it):
        self._it = it

    def __iter__(self):
        return self

    def next(self):
        # stops with StopIteration exception
        return Post(self._it.next())
