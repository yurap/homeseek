import tornado.ioloop
import tornado.web
from config import Config
from sources.group import Group
from sources.filter import Filter
from sources.stats import Stats
from sources.helpers import first_or_none
from sources.post import PostIterator
from pymongo import MongoClient
from lib.memnado.memnado import Memnado
from datetime import datetime


db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
m  = Memnado(Config.MEMCACHE_HOST, Config.MEMCACHE_PORT)


class AboutHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        def after_set(html):
            self.finish()

        def before_get(html):
            if html is not None:
                self.write(html)
                self.finish()
            else:
                html = self.render_string(
                    'about.html',
                    stats=Stats(PostIterator(db.posts.find())),
                    filter=Filter(None, {}),
                    now=datetime.now(),
                )
                self.write(html)
                m.set('about.html', html, after_set, expiry=300)

        m.get('about.html', before_get)


class SearchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render(
            'search.html',
            filter=Filter(db, {
                'price_min': first_or_none(self.get_query_arguments('min')),
                'price_max': first_or_none(self.get_query_arguments('max')),
                'station'  : first_or_none(self.get_query_arguments('m')),
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
