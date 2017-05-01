# coding: utf-8
import re
from abstract_parser import AbstractParser

class PriceParser(AbstractParser):
    _reg_braces = re.compile('\([^\)]+\)')
    _reg_nums = re.compile('[0-9]+|[5-9]')

    def _remove_text_in_braces(self, text):
        return self._reg_braces.sub(' ', text)

    def _get_candidates(self, post):
        text = post['text']
        text = self._remove_text_in_braces(text)
        if len(text) < 2:
            return []

        candidates = []
        for m in self._reg_nums.finditer(text):
            hyp = m.group()
            if len(hyp) > 3:
                hyp = str(int(hyp) / 1000)
            if int(hyp) < 5:
                continue

            candidates.append(self.Candidate(
                text[max(0, m.start()-20):min(m.start()+21, len(text))],
                int(hyp),
                m.start() - max(m.start() - 20, 0),
                m.group(),
            ))
        return candidates

    def _check_price_word(self, cand):
        w = u'(цена|стоимость|аренда)'
        pre  = re.compile(u'%s[^0-9!,\.]+%s' % (w, cand.guess), re.U | re.I)
        return pre.search(cand.context[:cand.pos + len(str(cand.guess))]) is not None

    def _check_deposit_word(self, cand):
        w = u'(депозит|залог|риэлтор|агент)'
        pre  = re.compile(u'%s[^0-9!,\.]+%s' % (w, cand.guess), re.U | re.I)
        return pre.search(cand.context[:cand.pos + len(str(cand.guess))]) is not None

    def _check_trailing_zeros(self, cand):
        r = re.compile(u'%s[^0-9а-яёa-z]?[05]00[^0-9]' % cand.guess, re.U | re.I)
        return r.search(cand.context) is not None

    def _check_thousands_letters(self, cand):
        r = re.compile(u'%s([,\.]5)?[^а-яё0-9a-z]?(тыс|т[ \.-]{,2}[р₽]|[кk][^а-яёa-z0-9])' % cand.guess, re.U | re.I)
        return r.search(cand.context) is not None

    def _check_candidate(self, c):
        if int(c.guess) <= 5 or int(c.guess) > 150:
            return False
        if self._check_price_word(c):
            return True
        if self._check_deposit_word(c):
            return False
        return self._check_trailing_zeros(c) or self._check_thousands_letters(c)        
