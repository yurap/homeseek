#!/usr/bin/env python
import sys
from pymongo import MongoClient, ASCENDING
from config import Config
from datetime import datetime
from sources.dup_finder import DupFinder
from sources.post import PostIterator
from datetime import datetime


if __name__ == '__main__':
    db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
    dup_finder = DupFinder([])

    to_delete = []
    for p in PostIterator(
        db.posts.find().sort(
            [('created_time', ASCENDING)]
        )
    ):
        if not dup_finder.check_and_add(p):
            to_delete.append(p._id)

    if len(to_delete) > 0:
        print >> sys.stderr, u'{}\tWill delete {} posts ...'.format(datetime.now(), len(to_delete))
        db.posts.delete_many({'_id':{'$in':to_delete}})
