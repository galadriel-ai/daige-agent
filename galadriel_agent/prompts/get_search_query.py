import random

from galadriel_agent.clients.database import DatabaseClient
from galadriel_agent.logging_utils import get_agent_logger
from galadriel_agent.models import AgentConfig

logger = get_agent_logger()


async def execute(agent: AgentConfig, database: DatabaseClient) -> str:
    all_search_topics = list(agent.search_queries.keys())
    used_search_topics = await database.get_latest_search_topics()
    filtered_search_topics = [
        t for t in all_search_topics if t not in used_search_topics
    ]
    try:
        topic = random.choice(filtered_search_topics)
        await database.add_latest_search_topic(topic)
        return random.choice(agent.search_queries.get(topic, []))
    except Exception:
        logger.error("Error choosing search query", exc_info=True)
        return ""
