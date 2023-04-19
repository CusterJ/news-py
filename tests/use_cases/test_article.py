import pytest
from unittest.mock import AsyncMock
from news.responses import (
    ResponseSuccess,
    ResponseFailure,
    ResponseTypes,
)
from news.domain.article import Article
from news.use_cases.article import article_count_use_case
from news.repository.mongo import MongoRepo

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_article_count_use_case_valid(mock_repo):
    mock_repo.count_documents.return_value = 10

    response = await article_count_use_case(mock_repo)

    assert bool(response) is True
    assert response.value == 10


@pytest.mark.asyncio
async def test_article_count_use_case_exception(mock_repo):
    mock_repo.count_documents.side_effect = Exception("Just an error message")

    response = await article_count_use_case(mock_repo)

    assert bool(response) is False
    assert response.value == {
        "type": ResponseTypes.SYSTEM_ERROR,
        "message": "Exception: Just an error message",
    }

