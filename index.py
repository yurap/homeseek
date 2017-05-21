import tornado.ioloop
import tornado.web
from config import Config
from sources.group import Group
from sources.filter import Filter
from sources.stats import Stats
from sources.helpers import first_or_none
from sources.post import PostIterator
from pymongo import MongoClient
from datetime import datetime
import lib.tornado_memcache.tornadoasyncmemcache as memcache


db  = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
ccs = memcache.ClientPool(['{}:{}'.format(Config.MEMCACHE_HOST, Config.MEMCACHE_PORT)], maxclients=100)


class AboutHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        ccs.get('about.html', callback=self._get_start)

    def _get_start(self, html):
        if html is None:
            html = self.render_string(
                'about.html',
                stats=Stats(PostIterator(db.posts.find())),
                filter=Filter(None, {}),
                now=datetime.now(),
            )
            ccs.set('about.html', html, time=600, callback=self._set_end)
        self.write(html)
        self.finish()

    def _set_end(self, data):
        pass


class SearchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render(
            'search.html',
            filter=Filter(db, {
                'price_min': first_or_none(self.get_query_arguments('min')),
                'price_max': first_or_none(self.get_query_arguments('max')),
                'stations' : first_or_none(self.get_query_arguments('ss')),
                'distance' : first_or_none(self.get_query_arguments('d')),
                'page'     : first_or_none(self.get_query_arguments('p')),
            }),
        )



app = tornado.web.Application([
    (r"/", AboutHandler),
    (r"/s", SearchHandler),
], debug=False, template_path=Config.TEMPLATES_FOLDER, static_path=Config.STATIC_FOLDER)


if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
