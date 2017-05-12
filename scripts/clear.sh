#!/usr/bin/env bash
set -ex
d=`date +%Y-%m-%d -d "14 days ago"`
mongo localhost/homeseek --eval "db.posts.remove({'created_time':{'\$lt':new Date('$d')}})"
