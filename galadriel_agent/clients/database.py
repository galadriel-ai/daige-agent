import json
import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import aiofiles

from galadriel_agent.logging_utils import get_agent_logger

logger = get_agent_logger()

TOPICS_FILE = "used_topics.json"
TWEETS_FILE = "tweets.json"
LATEST_TWEET_FILE = "latest_tweet.json"
SEARCH_TOPICS_FILE = "used_search_topics.json"


class DatabaseClient:
    topics_file_path: str
    max_topics_count: int
    max_search_topics_count: int

    tweets_file_path: str

    def __init__(
        self,
        data_dir: str = "data",
        max_topics_count: int = 5,
        max_search_topics_count: int = 7,
    ):
        self.max_topics_count = max_topics_count
        self.max_search_topics_count = max_search_topics_count

        os.makedirs(data_dir, exist_ok=True)
        self.topics_file_path = os.path.join(data_dir, TOPICS_FILE)
        self.tweets_file_path = os.path.join(data_dir, TWEETS_FILE)
        self.latest_tweet_file_path = os.path.join(data_dir, LATEST_TWEET_FILE)
        self.search_topics_file_path = os.path.join(data_dir, SEARCH_TOPICS_FILE)

    async def get_latest_used_topics(self) -> List[str]:
        try:
            return await _read_json_list(self.topics_file_path)
        except Exception:
            logger.error("Failed to get latest used topics", exc_info=True)
            return []

    async def add_topics(self, new_topics: List[str]) -> None:
        try:
            latest_topics = await self.get_latest_used_topics()
            latest_topics.extend(new_topics)
            latest_topics = latest_topics[self.max_topics_count * -1 :]
            await _write_json(self.topics_file_path, latest_topics)
        except Exception:
            logger.error("Failed to save latest used topics", exc_info=True)

    async def get_tweets(self) -> List[str]:
        try:
            return await _read_json_list(self.tweets_file_path)
        except Exception:
            logger.error("Failed to get tweets", exc_info=True)
            return []

    async def add_tweet_text(self, text: str) -> None:
        try:
            tweets = await self.get_tweets()
            tweets.append(text)
            await _write_json(self.tweets_file_path, tweets)
        except Exception:
            logger.error("Failed to save latest used topics", exc_info=True)

    async def get_latest_tweet(self) -> Optional[Dict]:
        try:
            return await _read_json_dict(self.latest_tweet_file_path)
        except Exception:
            logger.error("Failed to get tweets", exc_info=True)
            return None

    async def add_latest_tweet(self, tweet: Dict) -> None:
        try:
            await _write_json(self.latest_tweet_file_path, tweet)
        except Exception:
            logger.error("Failed to save latest used topics", exc_info=True)

    async def get_latest_search_topics(self) -> List[str]:
        if not os.path.exists(self.search_topics_file_path):
            logger.info(
                "Latest search topics file does not exist, returning an empty list"
            )
            return []
        try:
            return await _read_json_list(self.search_topics_file_path)
        except Exception:
            logger.error("Failed to get latest search topics", exc_info=True)
            return []

    async def add_latest_search_topic(self, topic: str) -> None:
        try:
            previous_topics = await self.get_latest_search_topics()
            previous_topics.append(topic)
            latest_topics = previous_topics[self.max_search_topics_count * -1 :]
            await _write_json(self.search_topics_file_path, latest_topics)
        except Exception:
            logger.error("Failed to save search topic", exc_info=True)


async def _read_json_list(file_path: str) -> List[str]:
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content)


async def _read_json_dict(file_path: str) -> Dict:
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content)


async def _write_json(file_path: str, content: Union[List, Dict]) -> None:
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(content, indent=4))
