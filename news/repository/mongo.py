import pprint
from pymongo.errors import BulkWriteError
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne

from news.domain.article import Article

class MongoRepo:
    def __init__(self, client):
        self.client = client
        self.articles = self.client.point.articles

    def _create_article_objects(self, results):
        return [
           Article(
                id=r["id"],
                title=r["title"]["short"],
                description=r["description"]["long"],
                date=r["dates"]["posted"],
                url=r["url"],
            )
            for r in results
        ]
    
    def _create_one_article_object(self, document):
        return Article(
                id=document["id"],
                title=document["title"]["short"],
                description=document["description"]["long"],
                date=document["dates"]["posted"],
                url=document["url"],
                )
    
    async def get_paginated_articles(self, skip: int, limit: int) -> list[Article]:
        arts = await self.articles.find({}).sort('dates.posted', -1).skip(skip).limit(limit).to_list(None)
        
        return self._create_article_objects(arts)
    

    async def get_article_by_id(self, id: str) -> Article:
        try:
            document = await self.articles.find_one({'id': id})
        except Exception as e:
            print("Mongo error: ", e)
            return {}
        return self._create_one_article_object(document)
    

    async def count_documents(self) -> int:
        try:
            n = await self.articles.count_documents({})
        except Exception:
            print("Unable to connect to the mongo.")
        return n


    async def update_one_article(self, art: Article) -> bool:
        try:
            result = await self.articles.update_one({'id': art.id}, {'$set': {'title.short': art.title, 'description.long': art.description}})
        except Exception as e:
            print("Mongo error: ", e)
            return False

        print(result.raw_result)
        return True

    async def bulk_write_articles(self, arts: list[Article]):
        requests = []

        for art in arts:
            requests.append(
                UpdateOne(filter={'id': art.id}, update={'$set': art._create_article_object_for_db()}, upsert=True)
            )

        try:
            await self.articles.bulk_write(requests, ordered=False)

        except BulkWriteError as bwe:
            pprint.pprint(bwe.details)
            return False

        # pprint.pprint(result.bulk_api_result)
        return True
