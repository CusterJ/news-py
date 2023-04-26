import json
from tornado.httpclient import HTTPRequest

from news.domain.article import Article

class ElasticRepo:
    def __init__(self, url, client):
        self.url = url
        self.http = client


    async def search(self, query: str, take: int, skip: int) -> dict:
        url = self.url + "_search"

        # print(f"search func -> es_url: {url}, TAKE = {take}, skip = {skip}")

        data = {
            "size": take,
            "from": skip,
            "query": {
                "multi_match": {
                "query": query,
                "fields": [
                    "title.short",
                    "description.long"
                ]
                }
            }
        }

        headers = {'Content-Type': 'application/json'}
        
        res = await self.http.fetch(url, method="POST", headers=headers, body=json.dumps(data))

        # print(res.code)
        return json.loads(res.body)


    async def update_one_article(self, art: Article) -> bool:
        es_url = self.url + "_doc/" + art.id

        data = {
            "id": art.id,
            "url": art.url,
            "title": {
                "short": art.title
                },
            "description": {
                "long": art.description
                },
            "dates": {
                "posted": art.date
                }
            }

        headers = {'Content-Type': 'application/json'}

        http_req = HTTPRequest(
            url=es_url,
            method="POST",
            headers=headers,
            body=json.dumps(data),
            )
        
        try:
            res = await self.http.fetch(http_req)
        except Exception as e:
            # sys.stderrr.write("Unable to connect to elastic:", e)
            print("Unable to connect to elastic:", e)
            return False
        
        if res.code != 200:
            return False
        return True
    
    async def bulk_write_articles(self, arts: list[Article]):
        requests = ""
        for art in arts:
            requests += json.dumps({ "index": { "_id": art.id }}) + "\n"
            requests += json.dumps(art._create_article_object_for_db()) + "\n"

        headers = {'Content-Type': 'application/json'}

        http_req = HTTPRequest(
            url=self.url+"_bulk",
            method="POST",
            headers=headers,
            body=requests,
            )
        
        try:
            res = await self.http.fetch(http_req)
        except Exception as exc:
            print("ES bulk write err", exc)
            return False
        
        if res.code != 200:
            return False
        
        return True

    async def check_index(self):
        es_url = self.url
        
        try:
            res = await self.http.fetch(es_url)
        except Exception as exc:
            print("check index error: ", exc)
            return False

        if res.code != 200:
            # create index
            ok = await self.create_index_and_mapping()
            if ok:
                return True
            return False
        
        return True

    async def create_index_and_mapping(self):
        print("es create_index_and_mapping")
        es_url = self.url
        print(es_url)

        index = {
            "settings": {
            "analysis": {
                "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_keywords": {
                    "type": "keyword_marker",
                    "keywords": [
                    "пример"
                    ]
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
                },
                "analyzer": {
                "rebuilt_russian": {
                    "tokenizer": "standard",
                    "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_keywords",
                    "russian_stemmer"
                    ]
                }
                }
            }
            },
            "mappings": {
            "properties": {
                "dates": {
                "properties": {
                    "posted": {
                    "type": "long"
                    }
                }
                },
                "description": {
                "properties": {
                    "long": {
                    "type": "text"
                    }
                }
                },
                "id": {
                "type": "text"
                },
                "title": {
                "properties": {
                    "short": {
                    "type": "text"
                    }
                }
                },
                "url": {
                "type": "text"
                }
            }
            }
        }


        headers = {'Content-Type': 'application/json'}

        http_req = HTTPRequest(
            url=es_url,
            method="PUT",
            headers=headers,
            body=json.dumps(index),
            )
        
        try:
            res = await self.http.fetch(http_req)
        except Exception as e:
            print("Unable to connect to elastic:", e)
            return False
        
        if res.code != 200:
            return False
        return True