# coding: utf-8
from abstract_parser import AbstractParser
import re
from helpers import split_to_phrases
from subway_parser import SubwayParser


class SubwayNearParser(AbstractParser):
    def __init__(self):
        self._subway_parser = SubwayParser()

    def _get_candidates(self, post):
        return [AbstractParser.Candidate(
            post['text'],
            1,
            0,
            post,
        )]

    def _check_minutes(self, text):
        pre = re.compile(u"([0-9]{1,2})(\-[а-я0-9]{,2})? ?мин(ут)?", re.U | re.I)
        post = re.compile(u"минут ([0-9]{1,2})(\-[а-я0-9]{,2})", re.U | re.I)
        return pre.search(text) is not None or post.search(text) is not None

    def _check_close(self, text):
        r = re.compile(u"неподал[её]ку|не ?(слишком|очень)? ?далеко|пешком|(шагов|пеш).{2} {,2}доступност|близко|рядом", re.U | re.I)
        return r.search(text) is not None

    def _check_metro_word(self, text):
        r = re.compile(u'метро|м\.', re.U | re.I)
        return r.search(text) is not None

    def _check_antimetro_word(self, text):
        r = re.compile(u'маршрутк|электричк', re.U | re.I)
        return r.search(text) is not None

    def _check_station(self, text):
        return self._subway_parser.check_text_has_station_name(text)

    def _check_candidate(self, c):
        phrases = split_to_phrases(c.context)
        close_seq = [self._check_minutes(phrase) or self._check_close(phrase) for phrase in phrases]
        for i in xrange(len(phrases)):
            phrase = phrases[i]
            if self._check_antimetro_word(phrase):
                return False
            if not self._check_metro_word(phrase) and not self._check_station(phrase):
                continue
            if True in close_seq[
                max(0,i-2):
                min(len(close_seq),i+3)
            ]:
                return True
        return False

    def debug(self, p):
        phrases = split_to_phrases(p['text'])
        for phrase in phrases:
            close = self._check_minutes(phrase) or self._check_close(phrase)
            metro = self._check_metro_word(phrase) or self._check_station(phrase)
            print u'* [{}] [{}] {}'.format(close, metro, phrase)
