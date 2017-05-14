import tornado.ioloop
import tornado.web
from config import Config
from sources.group import Group
from sources.filter import Filter
from sources.helpers import first_or_none
from pymongo import MongoClient


class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            'about.html',
            filter=Filter(None, {}),
        )


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        self.render(
            'search.html',
            filter=Filter(self.db, {
                'price_min': first_or_none(self.get_query_arguments('min')),
                'price_max': first_or_none(self.get_query_arguments('max')),
                'station'  : first_or_none(self.get_query_arguments('m')),
                'distance' : first_or_none(self.get_query_arguments('d')),
                'page'     : first_or_none(self.get_query_arguments('p')),
            }),
        )


db = MongoClient(Config.MONGO_URI)[Config.MONGO_DB]
app = tornado.web.Application([
    (r"/", AboutHandler),
    (r"/s", SearchHandler, dict(db=db)),
], debug=False, template_path=Config.TEMPLATES_FOLDER, static_path=Config.STATIC_FOLDER)


if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
