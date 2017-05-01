from collections import namedtuple


class AbstractParser(object):
    Candidate = namedtuple('Candidate', ['context', 'guess', 'pos', 'match'])

    def do(self, post):
        candidates = self._get_candidates(post)
        return set([c.guess for c in candidates if self._check_candidate(c)])

    def _get_candidates(self, text):
        raise NotImplemented()

    def _check_candidate(self, text):
        raise NotImplemented()
