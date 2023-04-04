import asyncio
import os
import motor
import tornado.web
# import sys
# sys.path.append('/home/max/Documents/Projects/news-py')

import application.handlers.handlers as handlers
import constants
from news.repository.mongo import MongoRepo
from news.repository.elastic import ElasticRepo


def make_app():
    return tornado.web.Application([
        (r"/", handlers.MainHandler),
        (r"/article/(.+)", handlers.ArticleHandler), 
        (r"/search?[A-Za-z0-9-]+", handlers.SearchHandler),
        (r"/static/images/(.*)",tornado.web.StaticFileHandler, {"path": "./static/images"},),
        (r"/static/css/(.*)",tornado.web.StaticFileHandler, {"path": "./static/css"},),
],
    template_path=os.path.join(os.path.dirname(__file__), "./templates/pages"),
    # static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug = True,
    autoreload = True)


async def main():
    app = make_app()

    # mongo connection
    mongo_conn = "mongodb://localhost:27017/"
    client = motor.motor_tornado.MotorClient(mongo_conn, serverSelectionTimeoutMS=5000)
    app.mongo_repo = MongoRepo(client)

    # elastic connection
    ES_URL = constants.ES_ARTS
    app.elastic_repo = ElasticRepo(ES_URL)

    # start web
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())