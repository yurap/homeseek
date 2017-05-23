#!/usr/bin/env python
# coding: utf-8
import json
import random
from sources.abstract_parser import AbstractParser
from sources.price_parser import PriceParser
from sources.subway_parser import SubwayParser
from sources.rent_parser import RentParser
from sources.subway_near_parser import SubwayNearParser


def load_markup(input_file):
    pool = []
    with open(input_file) as f:
        for line in f:
            pool.append(json.loads(line.rstrip()))
    return pool


def print_quality(pool, cls_parser, fn_get_correct):
    assert issubclass(cls_parser, AbstractParser)

    tp, fp, tn, fn = 0., 0., 0., 0.
    parser = cls_parser()

    for p in pool:
        guessed = set(parser.do(p))
        correct = set(fn_get_correct(p))
        tp += len(guessed & correct)
        fp += len(guessed - correct)
        fn += len(correct - guessed)

    precision = tp / (tp + fp)
    recall    = tp / (tp + fn)
    f1        = 2 * precision * recall / (precision + recall)
    print 'P  = {}'.format(precision)
    print 'R  = {}'.format(recall)
    print 'F1 = {}'.format(f1)


def print_errors(pool, cls_parser, fn_get_correct, limit=5, start=None):
    assert issubclass(cls_parser, AbstractParser)
    parser = cls_parser()

    ready = False
    for p in pool:
        if limit < 1:
            break
        if p["_id"]["$oid"] == start:
            ready = True
        if start is not None and not ready:
            continue

        guessed = set(parser.do(p))
        correct = set(fn_get_correct(p))
        if guessed != correct:
            limit -= 1
            print '\n== {} =='.format(p['_id']['$oid'])
            for cand in parser._get_candidates(p):
                print u'* [{}] {}'.format(cand.guess, cand.context)
            print u'correct :', u', '.join(sorted(map(unicode, list(correct))))
            print u'guessed :', u', '.join(sorted(map(unicode, list(guessed))))
            # parser.debug(p)
            # print p['text'].replace('\n', ' ')


def run_parse_test(name, pool, cls_parser, fn_check, debug):
    print '** {} **'.format(name)
    print_quality(pool, cls_parser, fn_check)
    if debug:
        print_errors(pool, cls_parser, fn_check)


if __name__ == '__main__':
    pool = load_markup('data/markup.json')

    run_parse_test(
        'PRICES',
        [post for post in pool if post['price'] > 0],
        PriceParser,
        lambda post: [int(post['price'] / 1000)],
        False,
    )

    run_parse_test(
        'SUBWAY',
        [post for post in pool if len(post['metro']) > 0],
        SubwayParser,
        lambda post: post['metro'],
        False,
    )

    run_parse_test(
        'SUBWAY NEAR',
        pool,
        SubwayNearParser,
        lambda post: [1] if u'метро-недалеко' in post['tags'] else [],
        False,
    )

    run_parse_test(
        'IS RENT',
        pool,
        RentParser,
        lambda post: [1] if u'сдать' in post['tags'] else [0],
        False,
    )

