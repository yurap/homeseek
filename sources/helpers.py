# coding: utf-8
import re


vowels = [u'а',u'е',u'и',u'о',u'у',u'ы',u'ю',u'я',]
def cut_ending_vowel(s):
    if s[-1] in vowels:
        return s[:-1]
    return s


re_sentence_splitter = re.compile(u'[\r\n]+|(?:[!?\.;](?:[ ]|([А-ЯЁA-Z])))', re.U)
def split_to_sentences(text):
    sentences = re_sentence_splitter.split(text)
    res = []
    prev_term = None
    for i in xrange(0, len(sentences), 2):
        prefix = '' if prev_term is None else prev_term.strip()
        new_sent = prefix + sentences[i].strip()
        if len(new_sent) > 0:
            res.append(new_sent)
        prev_term = sentences[i + 1] if i + 1 < len(sentences) else None
    return res


phone_re = re.compile(u'\+?[0-9][0-9 \-\(\)]{7,}[0-9]', re.I | re.U)
def remove_phones(s):
    return phone_re.sub(lambda m: u'[см. источник]', s)
