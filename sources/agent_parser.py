#coding:utf-8
from abstract_parser import AbstractParser
import re


class AgentParser(AbstractParser):
    def _get_candidates(self, post):
        return [AbstractParser.Candidate(
            post['text'],
            1,
            0,
            post,
        )]

    def _check_agent_word(self, text):
        r = re.compile(u'комм?исс?ия', re.I | re.U)
        return r.search(text) is not None

    def _check_alt_word(self, text):
        r = re.compile(u'много (других|альтернативных) (предложений|вариантов)', re.I | re.U)
        return r.search(text) is not None

    def _check_candidate(self, c):
        return self._check_agent_word(c.context) or self._check_alt_word(c.context)

    def check(self, post):
        return self.do(post) == {1}
