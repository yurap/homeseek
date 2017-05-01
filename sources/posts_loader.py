from post import Post
import sys
import json
import requests
import datetime


class AbstractLoader(object):
    def _load(self, group):
        raise NotImplemented()

    def _parse(self, json_data):
        raise NotImplemented()

    def _try_to_load(self, group):
        data = []
        try:
            data = self._load(group)
        except Exception as e:
            raise
            pass
        return data

    def get(self, group):
        posts_json = self._try_to_load(group)
        posts = []
        for post_json in posts_json:
            post = self._parse_post_data(post_json, group)
            if post is not None:
                posts.append(post)
        return posts


class VkLoader(AbstractLoader):
    def __init__(self, count):
        self._count = count

    def _load(self, group):
        r = requests.get(
            "https://api.vk.com/method/wall.get",
            params={
                'owner_id': group.id,
                'count': self._count,
                'offset': 0,
                'filter': 'all',
                'version': '5.52',
            }
        )
        return r.json()[u'response'][1:]

    def _parse_post_data(self, m, group):
        attachments = []
        if 'attachments' in m:
            for a in m['attachments']:
                if a['type'] == 'photo':
                    attachments.append(a['photo']['src_big'])
        return Post({
            'group_id'    : group.id,
            'post_id'     : m['id'],
            'text'        : '' if 'text' not in m else m['text'],
            'attachments' : attachments,
            'created_time': datetime.datetime.fromtimestamp(int(m['date']) + 3600 * 3),
            'tags': [],
        })


def fb_attachments(a):
    attachments = []
    for attach in a['data']:
        if 'media' in attach:
            attachments.append(attach['media']['image']['src'])
        elif 'subattachments' in attach:
            attachments += fb_attachments(attach['subattachments'])
    return attachments


class FbLoader(AbstractLoader):
    def __init__(self, token, count):
        self._count = count
        self._token = token

    def _load(self, group):
        r = requests.get(
            "https://graph.facebook.com/v2.5/{}/feed".format(group.id),
            params={
                'limit': self._count,
                'offset': 0,
                'filter': 'all',
                'fields': 'created_time,message,attachments',
                'access_token': self._token,
            }
        )
        return r.json()['data']

    def _parse_post_data(self, m, group):
        group_id, post_id = m['id'].split('_')
        time_format = '%Y-%m-%dT%H:%M:%S+0000'
        attachments = [] if 'attachments' not in m else fb_attachments(m['attachments'])
        return Post({
            'group_id'    : group.id,
            'post_id'     : post_id,
            'text'        : '' if 'message' not in m else m['message'],
            'attachments' : attachments,
            'created_time': datetime.datetime.strptime(m['created_time'], time_format) + datetime.timedelta(hours=3),
        })


class PostsLoader(object):
    def __init__(self, data_folder, count):
        self._vk = VkLoader(count)
        self._fb = FbLoader(open('{}/fb_token'.format(data_folder)).read().rstrip(), count)

    def get(self, g):
        loader = self._vk if g.check_is_vk() else self._fb
        return loader.get(g)
