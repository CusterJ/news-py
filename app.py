import asyncio
import os
import motor
import tornado.web

from dotenv import load_dotenv

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
    # load env variables
    load_dotenv(".env")
    MONGO_URL = os.getenv("MONGO_URL")
    ES_URL = os.getenv("ES_URL")

    # make application
    app = make_app()

    # mongo connection
    client = motor.motor_tornado.MotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    app.mongo_repo = MongoRepo(client)

    # elastic connection
    app.elastic_repo = ElasticRepo(ES_URL)

    # start web
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())