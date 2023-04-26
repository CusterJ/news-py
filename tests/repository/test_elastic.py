import pytest
from unittest.mock import AsyncMock

from news.domain.article import Article
from news.repository.elastic import ElasticRepo

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
async def test_check_index_success():
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 200

    repo = ElasticRepo(url, mock_client)
    check = await repo.check_index()

    assert check == True


@pytest.mark.asyncio
async def test_check_index_error():
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 404

    repo = ElasticRepo(url, mock_client)
    check = await repo.check_index()

    assert check == False


@pytest.mark.asyncio
async def test_create_index_and_mapping_success():
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 200

    repo = ElasticRepo(url, mock_client)
    create = await repo.create_index_and_mapping()

    mock_client.fetch.assert_awaited()
    mock_client.fetch.assert_awaited_once()
    mock_client.fetch.assert_called_once()
    assert create == True


@pytest.mark.asyncio
async def test_create_index_and_mapping_error():
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 404

    repo = ElasticRepo(url, mock_client)
    create = await repo.create_index_and_mapping()

    assert create == False


@pytest.mark.asyncio
async def test_bulk_write_articles_success(test_domain_articles_list):
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 200

    repo = ElasticRepo(url, mock_client)
    create = await repo.bulk_write_articles(test_domain_articles_list)

    assert create == True


@pytest.mark.asyncio
async def test_bulk_write_articles_error(test_domain_articles_list):
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 400

    repo = ElasticRepo(url, mock_client)
    create = await repo.bulk_write_articles(test_domain_articles_list)

    assert create == False


@pytest.mark.asyncio
async def test_update_one_article_success(test_domain_article):
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 200

    repo = ElasticRepo(url, mock_client)
    create = await repo.update_one_article(test_domain_article)

    assert create == True


@pytest.mark.asyncio
async def test_update_one_article_error(test_domain_article):
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 400

    repo = ElasticRepo(url, mock_client)
    create = await repo.update_one_article(test_domain_article)

    assert create == False


@pytest.mark.asyncio
async def test_search_valid_params():
    url = "http://elastic:9200/articles/"
    query = "test query"
    take = 10
    skip = 0
    mock_client = AsyncMock()
    mock_client.fetch.return_value.code = 200
    mock_client.fetch.return_value.body = b'{"hits": {"total": 1, "hits": [{"_source": {"title": "test title", "description": "test description"}}]}}'

    repo = ElasticRepo(url, mock_client)
    result = await repo.search(query, take, skip)

    mock_client.fetch.assert_called_once_with(
        'http://elastic:9200/articles/_search', 
        method='POST', 
        headers={'Content-Type': 'application/json'}, 
        body='{"size": 10, "from": 0, "query": {"multi_match": {"query": "test query", "fields": ["title.short", "description.long"]}}}',
    )

    assert isinstance(result, dict)
    assert "hits" in result
    assert "total" in result["hits"]
    assert "hits" in result["hits"]
    assert len(result["hits"]["hits"]) == 1
    assert "title" in result["hits"]["hits"][0]["_source"]
    assert "description" in result["hits"]["hits"][0]["_source"]


@pytest.mark.asyncio
async def test_search_invalid_params():
    url = "http://elastic:9200/articles/"
    query = None
    take = "invalid take"
    skip = "invalid skip"

    mock_client = AsyncMock()
    repo = ElasticRepo(url, mock_client)

    with pytest.raises(Exception):
        result = await repo.search(query, take, skip)