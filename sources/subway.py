# coding: utf-8
from subway_lines import all_subway_lines, all_conjunctions
from collections import defaultdict

class Subway(object):
    max_distance = 6

    def __init__(self):
        self._lines = all_subway_lines
        self._sid_to_conjunctions = {sid: conj for conj in all_conjunctions for sid in conj}
        self._sid_to_station = {station.id: station for line in self._lines for station in line.stations}
        self._sid_to_neighboors = self._build_sid_to_neighboors()

        self._name_index = defaultdict(list)
        for line in self._lines:
            for station in line.stations:
                self._name_index[station.name.lower()].append(station)
        # {station.name.lower(): station for line in self._lines for station in line.stations}

    def _build_sid_to_neighboors(self):
        sid_to_neighboors = {}
        for line in self._lines:
            for i in xrange(len(line.stations)):
                neighboors_ids = []
                if i > 0:
                    neighboors_ids.append(line.stations[i-1].id)
                if i + 1 < len(line.stations):
                    neighboors_ids.append(line.stations[i+1].id)
                sid_to_neighboors[line.stations[i].id] = neighboors_ids
        return sid_to_neighboors

    def get_lines(self):
        return self._lines

    def get_station_by_id(self, sid):
        if sid in self._sid_to_station:
            return self._sid_to_station[sid]
        return None

    def get_stations_by_name(self, name):
        if name in self._name_index:
            return self._name_index[name]
        return []

    def _find_neighboors_ids(self, station_ids):
        answer = set()
        for sid in station_ids:
            if sid in self._sid_to_conjunctions:
                answer |= set(self._sid_to_conjunctions[sid])
            if sid in self._sid_to_neighboors:
                answer |= set(self._sid_to_neighboors[sid])
        return answer

    def get_stations_by_distance(self, base_station_id, distance):
        station_ids = set([base_station_id])

        distance = min(distance, self.max_distance)
        while distance > 0:
            distance -= 1
            station_ids |= self._find_neighboors_ids(station_ids)

        stations = [self.get_station_by_id(sid) for sid in station_ids]
        stations = [s for s in stations if s is not None]
        return stations
