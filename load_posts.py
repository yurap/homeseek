#!/usr/bin/env python
import sys
from pymongo import MongoClient
from config import Config
from time import sleep
from datetime import datetime
from sources.group import Group
from sources.helpers import remove_phones
from sources.posts_loader import PostsLoader
from sources.rent_parser import RentParser
from sources.price_parser import PriceParser
from sources.subway_parser import SubwayParser
from sources.subway_near_parser import SubwayNearParser
from sources.dup_finder import DupFinder
from sources.post import PostIterator
from datetime import datetime, timedelta


def get_posts_it_from_db(db):
    time_bound = datetime.now() - timedelta(days=14)
    return PostIterator(db.posts.find({'created_time': {'$gt': time_bound}}))


def get_and_insert(anti=False):
    db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
    loader = PostsLoader(Config.DATA_FOLDER, 100)
    rent_parser = RentParser(anti)
    price_parser = PriceParser()
    subway_parser = SubwayParser()
    subway_near_parser = SubwayNearParser()
    dup_finder = DupFinder(get_posts_it_from_db(db))

    to_insert = []
    for g in Group.list():
        posts = loader.get(g)

        # this is important for dups date checker
        posts.sort(key=lambda p: p.created_time)

        accepted = 0
        skipped_by_price = 0
        skipped_by_date = 0
        skipped_by_dups = 0
        for p in posts:
            if not rent_parser.check(p):
                continue

            prices   = sorted(list(price_parser.do(p)))
            stations = sorted(list(subway_parser.do(p)))
            if len(prices) == 0 or len(stations) == 0:
                skipped_by_price += 1
                continue

            if p.check_is_old():
                skipped_by_date += 1
                continue

            if not dup_finder.check_and_add(p):
                skipped_by_dups += 1
                continue

            accepted += 1
            p.set('prices', prices)
            p.set('min_price', prices[0])
            p.set('max_price', prices[-1])
            p.set('subway', stations)
            p.set('subway_near', subway_near_parser.do(p) == {1})
            p.set('text', remove_phones(p.text))
            to_insert.append(p.to_json())

        print >> sys.stderr, u'{now}\t{accepted}/{skipped_by_price}/{skipped_by_date}/{skipped_by_dups}/{total}\t{gid}'.format(
            now=datetime.now(),
            accepted=accepted,
            total=len(posts),
            skipped_by_price=skipped_by_price,
            skipped_by_date=skipped_by_date,
            skipped_by_dups=skipped_by_dups,
            gid=g.id,
        )

    if len(to_insert) > 0:
        if not anti:
            db.posts.insert_many(to_insert)
        else:
            db.anti_posts.insert_many(to_insert)


if __name__ == '__main__':
    while True:
        try:
            get_and_insert(anti=False)
        except Exception as e:
            print >> sys.stderr, 'error!', str(e)
        print >> sys.stderr, '{}\twaiting for 600 seconds ...'.format(datetime.now())
        sleep(600)
