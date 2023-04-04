import tornado.web

from datetime import datetime

import constants

from news.domain.article import Article
from news.responses import ResponseTypes
from application.pagination import get_pagination
from news.use_cases.article import (
    article_list_use_case, 
    article_count_use_case,
    get_article_by_id_use_case,
    edit_article_by_id_use_case,
    search_use_case
    )

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        page = 1
        arg_page = self.get_argument('page', '1')
        if arg_page.isdigit():
            page = int(arg_page)
        else:
            raise tornado.web.HTTPError(404, "page value error")

        title = "News, Analysis, Politics, Business, Technology"

        mdb = self.application.mongo_repo
        arts = await article_list_use_case(mdb, page)
        total_arts = await article_count_use_case(mdb)

        if not arts or not total_arts:
            raise tornado.web.HTTPError(500, "", arts.message, total_arts.message)

        pages = get_pagination(page, constants.ARTICLES_TAKE, total_arts.value)
        pagination = {
            "current": str(page), 
            "pages": pages
        }

        self.render("news.html", title=title, arts=arts.value, pagination=pagination)

class ArticleHandler(tornado.web.RequestHandler):
    async def get(self, id):
        edit = self.get_argument('edit', False)

        mdb = self.application.mongo_repo
        art = await get_article_by_id_use_case(mdb, id)
        if art.type != ResponseTypes.SUCCESS:
            raise tornado.web.HTTPError(500)

        title = art.value.title
        date = datetime.fromtimestamp(art.value.date)

        self.render("article.html", title=title, art=art.value, date=date, edit=edit)

    async def post(self, id):
        art = Article(
            id=id,
            title=self.get_body_argument("title"),
            description=self.get_body_argument("description"),
            date=int(self.get_body_argument("posted")),
            url=self.get_body_argument("url")
        )

        if id == "" or art.title == "" or art.description == "":
            raise tornado.web.HTTPError(500, "error while saving article")

        # save to mongo
        mdb = self.application.mongo_repo
        mongo_ok = await edit_article_by_id_use_case(mdb, art)

        # save to elastic
        elastic = self.application.elastic_repo
        es_ok = await edit_article_by_id_use_case(elastic, art)

        # TODO: verify if mongo and es saved, undo the changes if not?

        # redirect to article(GET)
        if mongo_ok.value and es_ok.value:
            self.redirect(f"/article/{id}", False, 303)
        else:
            raise tornado.web.HTTPError(500, "error while saving article")
        

class SearchHandler(tornado.web.RequestHandler):
    async def get(self):
        query = self.get_argument('query', '')
        arg_page = self.get_argument('page', '1')
        if arg_page.isdigit():
            page = int(arg_page)
        else:
            raise tornado.web.HTTPError(400, reason='Ivalid argument')
        
        title = "Searching for: " + query

        # TODO: check if query is not empty
        # TODO: return from search_use_case list of Article and total results?

        elastic = self.application.elastic_repo
        res = await search_use_case(elastic, query, page)
        
        if res.type != ResponseTypes.SUCCESS:
            raise tornado.web.HTTPError(500)
        
        # all with get or not?
        arts = res.value.get("hits", []).get("hits")
        total = res.value.get("hits", 0)["total"]["value"]

        pages = get_pagination(page, constants.ARTICLES_TAKE, total)
        pagination = {
            "current": str(page), 
            "pages": pages
        }

        self.render("search.html", title=title, arts=arts, total=total, pagination=pagination)