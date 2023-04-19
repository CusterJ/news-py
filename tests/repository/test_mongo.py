import pytest
from unittest.mock import AsyncMock

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

@pytest.mark.asyncio
async def test_get_article_by_id(test_article, test_domain_article):
    mock_client = AsyncMock()
    mock_client.point.articles.find_one.return_value = test_article

    repo = MongoRepo(mock_client)
    article = await repo.get_article_by_id("1")
    print("print article", article)
    mock_client.point.articles.find_one.assert_called_once_with({"id": "1"})
    assert article == test_domain_article