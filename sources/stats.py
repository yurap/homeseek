from collections import defaultdict
from group import Group
from subway import Subway
from subway_lines import all_subway_lines


class Stats(object):
    def __init__(self, posts):
        self._groups_to_posts_per_day = defaultdict(lambda : defaultdict(int))
        self._prices = defaultdict(int)
        self._stations = defaultdict(int)
        subway = Subway()
        for p in posts:
            self._groups_to_posts_per_day[p.group_id][p.created_time.date()] += 1
            for price in p.prices:
                self._prices[price] += 1

            for station_name in p.subway:
                for station in subway.get_stations_by_name(station_name):
                    self._stations[station.id] += 1
        self._prices = [(price, self._prices[price]) for price in sorted(self._prices.keys())]
        # self._stations = [(station, self._stations[station]) for station in sorted(self._stations.keys(), key=lambda s: s.id)]
        # self._lines = [[(station.id, self._stations[station.id]) for station in line.stations] for line in all_subway_lines]

    def get_groups(self):
        return Group.list()

    def get_prices(self):
        return self._prices

    def get_lines(self):
        return all_subway_lines

    def get_station_count(self, sid):
        if sid in self._stations:
            return self._stations[sid]
        return 0

    def get_group_posts_per_day(self, gid):
        days_stats = self._groups_to_posts_per_day[gid]
        return [(d, days_stats[d]) for d in sorted(days_stats.keys())]

