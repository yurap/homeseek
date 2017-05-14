from collections import defaultdict
from group import Group


class Stats(object):
    def __init__(self, posts):
        self._groups_to_posts_per_day = defaultdict(lambda : defaultdict(int))
        self._prices = defaultdict(int)
        for p in posts:
            self._groups_to_posts_per_day[p.group_id][p.created_time.date()] += 1
            for price in p.prices:
                self._prices[price] += 1
        self._prices = [(price, self._prices[price]) for price in sorted(self._prices.keys())]

    def get_groups(self):
        return Group.list()

    def get_prices(self):
        return self._prices

    def get_group_posts_per_day(self, gid):
        days_stats = self._groups_to_posts_per_day[gid]
        return [(d, days_stats[d]) for d in sorted(days_stats.keys())]

