#!/usr/bin/env python
import sys
from pymongo import MongoClient, ASCENDING
from config import Config
from datetime import datetime
from sources.dup_finder import DupFinder
from sources.post import PostIterator
from datetime import datetime
from sources.rent_parser import RentParser
from sources.agent_parser import AgentParser


if __name__ == '__main__':
    db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
    dup_finder = DupFinder([])
    rent_parser = RentParser()
    agent_parser = AgentParser()

    to_delete = []
    deleted_by_dups = 0
    deleted_by_rent = 0
    deleted_by_agent = 0
    for p in PostIterator(
        db.posts.find().sort(
            [('created_time', ASCENDING)]
        )
    ):
        if not dup_finder.check_and_add(p):
            to_delete.append(p._id)
            deleted_by_dups += 1

        if not rent_parser.check(p):
            to_delete.append(p._id)
            deleted_by_rent += 1

        if agent_parser.check(p):
            to_delete.append(p._id)
            deleted_by_agent += 1

    if len(to_delete) > 0:
        print >> sys.stderr, u'{}\tWill delete {}(dups) / {}(rent) / {}(agent) / {}(total) posts ...'.format(
            datetime.now(),
            deleted_by_dups,
            deleted_by_rent,
            deleted_by_agent,
            len(to_delete),
        )
        db.posts.delete_many({'_id':{'$in':to_delete}})
