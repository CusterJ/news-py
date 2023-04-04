from news.responses import (
    ResponseSuccess,
    ResponseFailure,
    ResponseTypes,
)
from news.domain.article import Article
import constants

async def article_list_use_case(repo, page: int):
    limit = constants.ARTICLES_TAKE
    skip = 0

    if page >= 2:
        skip = (page-1) * limit 

    try:
        arts = await repo.get_paginated_articles(skip, limit)
        return ResponseSuccess(arts)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)


async def article_count_use_case(repo):
    try:
        total = await repo.count_documents()
        return ResponseSuccess(total)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)


async def get_article_by_id_use_case(repo, id):
    try:
        art = await repo.get_article_by_id(id)
        return ResponseSuccess(art)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)


async def edit_article_by_id_use_case(repo, art: Article):
    try:
        ok = await repo.update_one_article(art)
        return ResponseSuccess(ok)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)
    
    
async def search_use_case(repo, query: str, page: int):
    TAKE = constants.ARTICLES_TAKE

    if page <=1:
        skip = 0
    else:
        skip = (page-1) * TAKE

    try:
        response = await repo.search(query, TAKE, skip)
        return ResponseSuccess(response)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)