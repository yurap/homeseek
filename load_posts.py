#!/usr/bin/env python
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
from sources.dup_finder import DupFinder


def get_and_insert():
    db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
    loader = PostsLoader(Config.DATA_FOLDER, 100)
    rent_parser = RentParser()
    price_parser = PriceParser()
    subway_parser = SubwayParser()
    dup_finder = DupFinder(db)

    to_insert = []
    for g in Group.list():
        posts = loader.get(g)

        accepted = 0
        for p in posts:
            if not rent_parser.check(p):
                continue

            prices   = sorted(list(price_parser.do(p)))
            stations = sorted(list(subway_parser.do(p)))
            if len(prices) == 0 or len(stations) == 0:
                continue

            if not dup_finder.check_is_ok(p):
                continue

            if p.check_is_old():
                continue

            accepted += 1
            dup_finder.add(p)
            p.set('prices', prices)
            p.set('min_price', prices[0])
            p.set('max_price', prices[-1])
            p.set('subway', stations)
            p.set('text', remove_phones(p.text))
            to_insert.append(p.to_json())

        print u'{}\t{}/{}\t{}'.format(datetime.now(), accepted, len(posts), g.name)

    if len(to_insert) > 0:
        db.posts.insert_many(to_insert)


if __name__ == '__main__':
    while True:
        try:
            get_and_insert()
        except Exception as e:
            print 'error!', str(e)
        print '{}\twaiting for 600 seconds ...'.format(datetime.now())
        sleep(600)
