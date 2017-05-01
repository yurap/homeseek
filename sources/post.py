import random
from helpers import split_to_sentences
from datetime import datetime


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

    def check_is_old(self):
        d = datetime.now() - self.created_time
        return d.total_seconds() / 3600. / 24 > 14
