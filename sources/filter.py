from group import Group
from subway import Subway
from post import Post
from pymongo import DESCENDING


class Filter(object):
    overall_min_price = 5000
    overall_max_price = 200000
    posts_per_page    = 20

    def cut_price(self, price):
        return max(min(price, self.overall_max_price), self.overall_min_price)

    def safe_get_int_value(self, data, key, default_value):
        if key not in data or data[key] is None or not data[key].isnumeric():
            return int(default_value)
        return int(data[key])

    def __init__(self, db, data):
        self.gid_to_group = {g.id: g for g in Group.list()}

        self.db = db
        self.subway = Subway()

        self.price_max  = self.cut_price(self.safe_get_int_value(data, 'price_max', self.overall_max_price))
        self.price_min  = self.cut_price(self.safe_get_int_value(data, 'price_min', self.overall_min_price))
        self.station_id = self.safe_get_int_value(data, 'station', 0)
        self.distance   = self.safe_get_int_value(data, 'distance', 3)

        self.station_ids = [] if 'stations' not in data or data['stations'] is None else data['stations'].rstrip('_').split('_')
        self.station_ids = set([int(sid) for sid in self.station_ids if sid.isnumeric()])
        self.stations    = [self.subway.get_station_by_id(sid) for sid in self.station_ids]

        self.page       = 1 if 'page' not in data or data['page'] is None else max(int(data['page']), 1)
        self.start      = (self.page - 1) * self.posts_per_page

        if self.db is not None:
            posts_it = self._find()
            self.total_posts = posts_it.count()
            self.posts = [Post(json_post) for json_post in posts_it]

            self.total_pages = self.total_posts / self.posts_per_page + (1 if self.total_posts % self.posts_per_page > 0 else 0)
            # self.pages = ['%02d' % i for i in xrange(1, self.total_pages + 1)]
            self.pages = [i for i in xrange(1, self.total_pages + 1)]

    def _find(self):
        query = {}
        query['min_price'] = {'$lte': self.price_max / 1000}
        query['max_price'] = {'$gte': self.price_min / 1000}
        if len(self.stations) > 0:
            query['subway'] = {'$in': [s.name.lower() for s in self.stations]}
        return self.db.posts \
            .find(query) \
            .skip(self.start) \
            .limit(self.posts_per_page) \
            .sort([('created_time', DESCENDING)])

    def get_groups(self):
        return Group.list()

    def get_group_by_id(self, gid):
        if gid in self.gid_to_group:
            return self.gid_to_group[gid]

    def get_subway_lines(self):
        return self.subway.get_lines()

    def check_subway_station_on(self, station):
        return False

    def skip_page(self, p):
        return abs(int(p) - int(self.page)) >= 3

    def get_url_for_page(self, p):
        return '/s?min={}&max={}&d={}&m={}&p={}'.format(
            self.price_min,
            self.price_max,
            self.distance,
            self.station_id,
            p,
        )

