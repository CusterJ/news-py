import pytest
from unittest.mock import AsyncMock, MagicMock

from news.repository.mongo import MongoRepo
from news.domain.article import Article

@pytest.fixture
def test_article():
    return {
        "id": "9bff3d3d-1549-4b65-b75f-1ad6105dba42",
        "url": "vypusknik-akademii-fbr-stal-zamestitelem-gensekretaria-mvd-moldovy",
        "title": {
        "short": "Выпускник Академии ФБР стал заместителем генсекретаря МВД Молдовы"
        },
        "description": {
        "long": "description_long"
        },
        "dates": {
        "posted": 1681308480
        }
    }

@pytest.fixture
def test_domain_article():
    return Article(
        id="9bff3d3d-1549-4b65-b75f-1ad6105dba42",
        title="Выпускник Академии ФБР стал заместителем генсекретаря МВД Молдовы",
        description="description_long",
        date=1681308480,
        url="vypusknik-akademii-fbr-stal-zamestitelem-gensekretaria-mvd-moldovy"
    )

@pytest.fixture
def test_articles_list():
    arts = [
        {
            "id": "9bff3d3d-1549-4b65-b75f-1ad6105dba42",
            "url": "vypusknik-akademii-fbr-stal-zamestitelem-gensekretaria-mvd-moldovy",
            "title": {
            "short": "Выпускник Академии ФБР стал заместителем генсекретаря МВД Молдовы"
            },
            "description": {
            "long": "description_long"
            },
            "dates": {
            "posted": 1681308480
            }
        },
        {
            "id": "9bff3d3d-1549-4b65-b75f-1ad6105dba44",
            "url": "url_2",
            "title": {
            "short": "title_short_2"
            },
            "description": {
            "long": "description_long_2"
            },
            "dates": {
            "posted": 1681308482
            }
        }
    ]
    return arts

@pytest.fixture
def test_domain_articles_list():
    return [
    Article(
        id="9bff3d3d-1549-4b65-b75f-1ad6105dba42",
        title="Выпускник Академии ФБР стал заместителем генсекретаря МВД Молдовы",
        description="description_long",
        date=1681308480,
        url="vypusknik-akademii-fbr-stal-zamestitelem-gensekretaria-mvd-moldovy"
        ),
    Article(
        id="9bff3d3d-1549-4b65-b75f-1ad6105dba44",
        title="title_short_2",
        description="description_long_2",
        date=1681308482,
        url="url_2"
        )
    ]


@pytest.mark.asyncio
async def test_get_article_by_id(test_article, test_domain_article):
    mock_client = AsyncMock()
    mock_client.point.articles.find_one.return_value = test_article

    repo = MongoRepo(mock_client)
    article = await repo.get_article_by_id("1")

    mock_client.point.articles.find_one.assert_called_once_with({"id": "1"})
    assert article == test_domain_article

@pytest.mark.asyncio
async def test_count_documents():
    mock_count = 6022
    mock_client = AsyncMock()
    mock_client.point.articles.count_documents.return_value = mock_count

    repo = MongoRepo(mock_client)
    count = await repo.count_documents()

    mock_client.point.articles.count_documents.assert_called_once_with({})
    assert count == mock_count

@pytest.mark.asyncio
async def test_get_paginated_articles(test_articles_list, test_domain_articles_list):
    skip = 0
    limit = 15

    mock_find = MagicMock()
    mock_sort = MagicMock()
    mock_skip = MagicMock()
    mock_limit = MagicMock()
    mock_to_list = AsyncMock()

    mock_to_list.to_list.return_value=test_articles_list
    mock_limit.limit.return_value = mock_to_list
    mock_skip.skip.return_value = mock_limit
    mock_sort.sort.return_value = mock_skip
    mock_find.point.articles.find.return_value = mock_sort
    
    repo = MongoRepo(mock_find)
    arts = await repo.get_paginated_articles(skip=skip, limit=limit)

    mock_find.point.articles.find.assert_called_once_with({})
    mock_sort.sort.assert_called_once_with('dates.posted', -1)
    mock_skip.skip.assert_called_once_with(skip)
    mock_limit.limit.assert_called_once_with(limit)
    mock_to_list.to_list.assert_called_once_with(None)
    assert arts == test_domain_articles_list