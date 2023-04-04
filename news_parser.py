import os
import motor
import constants
import http.client
import asyncio
import json
import time
import motor.motor_asyncio

from datetime import datetime, timedelta

from news.repository.mongo import MongoRepo
from news.repository.elastic import ElasticRepo
from news.domain.article import Article


class Parser:
    def __init__(self, mongo_repo, es_repo):
        self.mdb = mongo_repo
        self.es = es_repo
        self.take_from_site: int = 3
        self.parsed_arts: int = 0
        self.date_now: int = int(time.time()) 
        self.date_db: int = 0
        self.date_site: int = 0
        self.date_last_list_article: int = 0
        self.no_arts_timedelta_weeks: float = 1
        self.article_ids = [] 
        self.articles_list = []

    def _create_one_article_object(self, art):
        return Article(
                id=art["data"]["content"]["id"],
                title=art["data"]["content"]["title"]["short"],
                description=art["data"]["content"]["description"]["long"],
                date=art["data"]["content"]["dates"]["posted"],
                url=art["data"]["content"]["url"],
            )

    def start_parser(self):
        pass
    
    def get_last_article_date_from_mongo(self) -> int:
        # Get async func from sync
        async def mdb_paginated_articles():
            arts = await self.mdb.get_paginated_articles(skip=0, limit=1)
            return arts
        arts = asyncio.run(mdb_paginated_articles())

        # try to get date from list
        try:
            date = arts[0].date
        except Exception as e:
            print("Get date from list of arts from mdb error: ", e)
            # if mongo is empty, set default db date to take arts from site  
            if str(e) == str("list index out of range"): 
                date_from = datetime.today() - timedelta(weeks=self.no_arts_timedelta_weeks)
                self.date_db = int(date_from.timestamp())
                return
            else:
                os._exit(1)

        self.date_db = date # 1678050000

    def get_last_article_date_from_site(self):
        conn = http.client.HTTPSConnection("point.md")

        headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json" 
        }

        pld_query = "query contents($projectId: String!, $lang: String = \"ru\", $take: Int = 30, $skip: Int, $dateto: Int) { contents( project_id: $projectId lang: $lang take: $take skip: $skip posted_date_to: $dateto ) { id title { short } dates { posted } } }"
        pld = {
            "query": pld_query,
            "variables": {
                "lang":"ru",
                "take": 1,
                "projectId":"5107de83-f208-4ca4-87ed-9b69d58d16e1",
                "postedDateTo":self.date_now}
        }

        conn.request("POST", "/graphql", json.dumps(pld), headersList)
        response = conn.getresponse()
        result = response.read()

        data = json.loads(result)

        self.date_site = int(data.get("data").get("contents")[0].get("dates").get("posted"))
        self.date_last_list_article = self.date_site + 1
       
    def get_articles_list_by_date_from_site(self):
        conn = http.client.HTTPSConnection("point.md")

        headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json" 
        }

        pld_query = "query contents($projectId: String!, $lang: String = \"ru\", $take: Int = 30, $skip: Int, $dateto: Int) { contents( project_id: $projectId lang: $lang take: $take skip: $skip posted_date_to: $dateto ) { id title { short } dates { posted } } }"
        pld = {
            "query": pld_query,
            "variables": {
                "lang":"ru",
                "take":self.take_from_site,
                "projectId":"5107de83-f208-4ca4-87ed-9b69d58d16e1",
                "dateto":self.date_last_list_article
                }
        }

        conn.request("POST", "/graphql", json.dumps(pld), headersList)
        response = conn.getresponse()
        result = response.read()

        data = json.loads(result)

        arts = data.get("data").get("contents")

        for art in arts:
            id = art.get("id")
            self.article_ids.append(id)

        self.date_last_list_article = int(data.get("data").get("contents")[len(arts)-1].get("dates").get("posted"))

    def _get_article_by_id_from_site(self, art_id) -> Article:
        conn = http.client.HTTPSConnection("point.md")

        headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json" 
        }

        pld_query = "query content($id: String!) { content( id: $id ) { id url title{ short } description{ long } dates{ posted } } }"
        pld = {
            "query": pld_query,
            "variables": {
                "id": art_id
                }
        }

        conn.request("POST", "/graphql", json.dumps(pld), headersList)
        response = conn.getresponse()
        result = response.read()

        return self._create_one_article_object(json.loads(result))

    def save_article_list_to_dbs(self):
        for art_id in self.article_ids:
            art = self._get_article_by_id_from_site(art_id)
            self.articles_list.append(art)
            # print(art.get("data").get("content").get("title").get("short"))
            # result = self.mdb.save_one_article(art)

        async def run_sync():
            result = await self.mdb.bulk_write_articles(self.articles_list)
            # result = await self.mdb.save_one_article(art)
            # result = await self.mdb.get_server_info()
            return result
        result = asyncio.run(run_sync())
        print(result)
        # print(self.articles_list)

        # clear article_ids list and articles_list variables
        self.parsed_arts += len(self.articles_list)
        self.article_ids = []
        self.articles_list = []


def main():
    # mongo connection
    mongo_conn = constants.MONGO
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_conn, serverSelectionTimeoutMS=5000)
    # client = motor.MotorClient(mongo_conn, serverSelectionTimeoutMS=5000)
    mdb = MongoRepo(client)

    # elastic connection
    ES_URL = constants.ES_ARTS
    es = ElasticRepo(ES_URL)

    # init parser
    pr = Parser(mdb, es)

    # TODO: rewrite this func
    # why does this break the worker?
    # pr.get_last_article_date_from_mongo()

    while True:
        pr.get_last_article_date_from_mongo()
        pr.get_last_article_date_from_site()
        print("mongo_date  = ", pr.date_db, datetime.fromtimestamp(pr.date_db))
        print("date_site   = ", pr.date_site, datetime.fromtimestamp(pr.date_site))

        if pr.date_db < pr.date_site:
            pr.get_articles_list_by_date_from_site()
            pr.save_article_list_to_dbs()
            time.sleep(1)

            while pr.date_db < pr.date_last_list_article:
                pr.get_articles_list_by_date_from_site()
                pr.save_article_list_to_dbs()
                time.sleep(1)

        print("date_last_list_article = ", pr.date_last_list_article, datetime.fromtimestamp(pr.date_last_list_article))
        print("mongo_date  = ", pr.date_db, datetime.fromtimestamp(pr.date_db))
        print("parsed_arts = ", pr.parsed_arts)
        time.sleep(60)


if __name__ == "__main__":
    # asyncio.run(main())
    main()