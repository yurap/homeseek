from collections import defaultdict
from post import Post


class DupFinder(object):
    def __init__(self, posts):
        self._hashes = set()
        # self._hashes = defaultdict(list)
        self._group_to_latest_dt = {}
        self._checksums = set()
        for p in posts:
            self._add_post(p)

    def _update_latest_group_dt(self, p):
        if p.group_id not in self._group_to_latest_dt:
            self._group_to_latest_dt[p.group_id] = p.created_time
        if p.created_time > self._group_to_latest_dt[p.group_id]:
            self._group_to_latest_dt[p.group_id] = p.created_time

    def _update_hashes(self, p):
        self._hashes |= set(p.get_sentence_hashes())
        # for h in p.get_sentence_hashes(sample=2):
        #     self._hashes[h].append(p)

    def _update_checksums(self, p):
        self._checksums.add(p.get_checksum())

    def _add_post(self, p):
        self._update_latest_group_dt(p)
        self._update_hashes(p)
        self._update_checksums(p)

    def _check_by_group_dt(self, p):
        if p.group_id in self._group_to_latest_dt:
            if self._group_to_latest_dt[p.group_id] > p.created_time:
                return False
        return True

    def _check_by_sentence_hashes(self, p):
        total_matched = 0
        for h in p.get_sentence_hashes():
            if h in self._hashes:
                total_matched += 1
            if total_matched > 1:
                return False
        return True

    def _check_by_checksum(self, p):
        return p.get_checksum() not in self._checksums

    def _check_post_is_unique(self, p):
        if not self._check_by_group_dt(p):
            return False
        if not self._check_by_checksum(p):
            return False
        if not self._check_by_sentence_hashes(p):
            return False
        return True

    # def find_dup(self, p):
    #     for h in p.get_sentence_hashes():
    #         if h in self._hashes:
    #             return self._hashes[h]
    #     return None

    def check_and_add(self, p):
        if not self._check_post_is_unique(p):
            return False
        self._add_post(p)
        return True
