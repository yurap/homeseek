# coding: utf-8
import re
from itertools import combinations
from subway_lines import all_subway_lines
from helpers import cut_ending_vowel
from abstract_parser import AbstractParser


def _prepare_word_pattern(word):
    word = word \
        .replace(u'-', u'[\s\-]?') \
        .replace(u'имени', u'им[^ ]+') \
        .replace(u'бульвар', u'б(ульва|\-)р') \
        .replace(u'ё', u'[её]')
    word = cut_ending_vowel(word)
    word = cut_ending_vowel(word)
    return word + u'([аеиоуыюя][а-я]?)?'


def _prepare_station_reg(station_name):
    pattern = '' u'\s+'.join(
        [_prepare_word_pattern(w) for w in station_name.split() if w != u'улица']
    )
    pattern = u'[^а-яё]{}[^а-яё]'.format(pattern)
    # print pattern
    return re.compile(pattern, re.U | re.I)


class StationReg(object):
    def __init__(self, station):
        self.station = station
        self.reg = _prepare_station_reg(station.name.lower())

    def get_candidates(self, text):
        candidates = []
        for m in self.reg.finditer(text + ' '):
            c = AbstractParser.Candidate(
                text[m.start()-20:m.start()+len(m.group()) + 21].lower(),
                self.station.name.lower(),
                m.start() - max(m.start() - 20, 0),
                m.group(),
            )
            candidates.append(c)
        return candidates


class SubwayParser(AbstractParser):
    def __init__(self):
        self.subway_regs = self._build_subway_regs()

    def _build_subway_regs(self):
        stations = [s for line in all_subway_lines for s in line.stations]
        stations.sort(key=lambda s: s.name)
        return [StationReg(s) for s in stations]

    def _get_candidates(self, post):
        return self._get_candidates_from_text(post['text'])

    def _get_candidates_from_text(self, text):
        candidates = []
        for r in self.subway_regs:
            candidates += r.get_candidates(text)
        return self._drop_similar(candidates)

    def _drop_similar(self, candidates):
        # this is dirty
        names = set([c.guess for c in candidates])
        kicked = {
            u'сокол': u'сокольники',
            u'октябрьская': u'октябрьское поле',
        }
        check_kicked = lambda c: c.guess in kicked and kicked[c.guess] in names
        return [c for c in candidates if not check_kicked(c)]

    def _check_metro_word(self, c):
        w = u'метро|м\.|м {}'.format(c.guess)
        reg = re.compile(w, re.I | re.U)
        return reg.search(c.context) is not None

    def _check_park_word(self, c):
        w = u'парк|проспект|улица|ул\.?|проезд|перекресток'
        r = re.compile(w, re.I | re.U)
        in_context = r.search(c.context) is not None
        in_guess = r.search(c.guess) is not None

        if not in_guess and in_context:
            return True
        return False

    def _check_candidate(self, c):
        if self._check_metro_word(c):
            return True
        if self._check_park_word(c):
            return False
        return True

    def check_text_has_station_name(self, text):
        cands = self._get_candidates_from_text(text)
        # print '!', len(cands)
        for c in cands:
            # print '$', c.context
            if self._check_candidate(c):
                return True
        return False
