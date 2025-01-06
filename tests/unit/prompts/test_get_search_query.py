from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from galadriel_agent.prompts import get_search_query


async def test_success():
    agent = MagicMock()
    agent.search_queries = {
        "key": ["value"],
    }
    db = AsyncMock()
    db.get_latest_search_topics.return_value = []

    result = await get_search_query.execute(agent, db)
    assert result == "value"


async def test_excludes_used_topic():
    agent = MagicMock()
    agent.search_queries = {
        "key1": ["value1"],
        "key2": ["value2"],
    }
    db = AsyncMock()
    db.get_latest_search_topics.return_value = ["key1"]

    result = await get_search_query.execute(agent, db)
    assert result == "value2"
