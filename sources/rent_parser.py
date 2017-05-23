# coding: utf-8
import re
import os
import pickle
from helpers import split_to_sentences
from abstract_parser import AbstractParser


def _flat_regex(rooms):
    sep        = u'[ \.]?'
    prefixes   = [u'(1-?|одно)', u'(2-?[хx]?|двух)', u'(3-?[хx]?|тр[её]х)', u'(4-?[хx]?|четыр[её]х)']
    additional_suffixes = [u'студи(я|ю|и|е)|однушк', u'двушк', u'тр[её]шк', u'четыр[её]шк']
    reg_str = u'(({prefix}){nn}{sep}({adj}){nn}{sep}({suffix}))|(({additional})(а|ы|и|е|у|ой))'.format(
        nn     = '?' if rooms == 0 else '',
        sep    = sep,
        prefix = prefixes[rooms - 1] if 1 <= rooms <= 4 else '|'.join(prefixes),
        adj    = u'((к|ком|комн)\.?)|комнатн(ая|ой|ую)',
        suffix = u'кв[^ ]+',
        additional = additional_suffixes[rooms - 1] if 1 <= rooms <= 4 else u'|'.join(additional_suffixes),
    )
    if rooms == 4:
        reg_str += u'|(4 комнаты)'
    return reg_str


class RentParser(AbstractParser):
    _model_file = os.path.dirname(os.path.abspath(__file__)) + '/../data/rent.adaboost.clf'
    _anti_model_file = os.path.dirname(os.path.abspath(__file__)) + '/../data/antirent.gradboost.clf'

    # todo: make this pretty
    fnames = ['attachments', 'digits', 'flat', 'give', 'locals', 'money', 'nboor', 'offtop', 'price', 'question_marks', 'room', 'sents', 'share', 'take']
    def __init__(self, anti=False):
        f = self._anti_model_file if anti else self._model_file
        self._clf = pickle.loads(open(f).read())

    def _classify(self, post):
        features = self._calc_features(post)
        return self._clf.predict([features])[0]

    def _get_candidates(self, post):
        return [self.Candidate(post, self._classify(post), 0, 0)]

    def _check_candidate(self, c):
        return True

    def _calc_features(self, post):
        features = []
        sents = split_to_sentences(post['text'])
        for f in self.fnames:
            features.append(getattr(self, 'calc_' + f)(post, sents))
        return features

    def _re(self, r, sents):
        total = 0
        for s in sents:
            total += 1 if r.search(s) is not None else 0
        return total

    def calc_sents(self, post, sents):
        return len(sents)
    def calc_attachments(self, post, sents):
        return len(post['attachments'])
    def calc_locals(self, post, sents):
        return self._re(re.compile(u'локалс|лоукалс|locals', re.U | re.I), sents)
    def calc_share(self, post, sents):
        return self._re(re.compile(u'(нужен|подели|скаж|дайте)[^ ]* (контакт|доступ)', re.U | re.I), sents)
    def calc_question_marks(self, post, sents):
        return post['text'].count('?')
    def calc_offtop(self, post, sents):
        return self._re(re.compile(u'оффтоп|тестируем|самовывоз|отдам|прода[^ ]+|приобрет[её]м|посовету[^ ]+|куп(лю|им)', re.U | re.I), sents)
    def calc_price(self, post, sents):
        return self._re(re.compile(u'цена', re.U | re.I), sents)
    def calc_money(self, post, sents):
        return self._re(re.compile(u'бюджет', re.U | re.I), sents)
    def calc_digits(self, post, sents):
        counter = 0
        for c in post['text']:
            if c.isdigit():
                counter += 1
        return counter
    def calc_flat(self, post, sents):
        return self._re(re.compile(_flat_regex(0), re.U | re.I), sents)
    def calc_room(self, post, sents):
        counter = 0
        r1 = re.compile(u'сда[еёю]|(сним|ищ)(у|ем|ет)|разыск|поиск|найти|о?свобо|изолированная', re.I | re.U)
        r2 = re.compile(u'комнат[ауые]', re.I | re.U)
        for s in sents:
            has_word = False
            for w in s.split():
                if r1.match(w):
                    has_word = True
                if has_word and r2.match(w):
                    counter += 1
                    break
        return counter
    def calc_nboor(self, post, sents):
        return self._re(re.compile(u'подселени|(найти|ищ(у|ем|ет)) ([^ ]+ )*(сосед(а|ей|ку|кой)|замену)', re.U | re.I), sents)
    def calc_give(self, post, sents):
        return self._re(re.compile(u'сда([её]м|[её]ть?(ся)?|ю|ют|дут|м)', re.U | re.I), sents)
    def calc_take(self, post, sents):
        return self._re(re.compile(u'(сним|ищ)(у|ем|ет)|разыск[^ ]+|поиск', re.U | re.I), sents)

    def check(self, post):
        return list(self.do(post))[0] == 1
