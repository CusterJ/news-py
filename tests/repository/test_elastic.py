import pytest
from unittest.mock import patch, AsyncMock

from news.repository.elastic import ElasticRepo

@pytest.mark.asyncio
async def test_check_index_success():
    url = "http://elastic:9200/articles/"

    mock_client = AsyncMock()
    mock_client.http_client.fetch = True

    repo = ElasticRepo(url, mock_client)
    res = await repo.check_index()

    assert res == True