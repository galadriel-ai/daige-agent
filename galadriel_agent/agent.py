import asyncio
import json
import random
from pathlib import Path
from typing import List

from galadriel_agent.clients.galadriel import GaladrielClient
from galadriel_agent.clients.perplexity import PerplexityClient
from galadriel_agent.clients.twitter import TwitterClient
from galadriel_agent.clients.twitter import TwitterCredentials
from galadriel_agent.logging_utils import get_agent_logger
from galadriel_agent.logging_utils import init_logging
from galadriel_agent.models import AgentConfig

logger = get_agent_logger()

PROMPT_TEMPLATE = """# Areas of Expertise
{{knowledge}}

# About {{agent_name}} (@{{twitter_user_name}}):
{{bio}}
{{lore}}
{{topics}}

{{post_directions}}

# Task: Generate a post in the voice and style and perspective of {{agent_name}} @{{twitter_user_name}}.
Write a 1-3 sentence post that is tech-savvy based on the latest trending news you read, here's what you read:

"{{perplexity_content}}"

Here are the citations, where you read about this:
{{perplexity_sources}}

You have to address what you read directly. Be brief, and concise, add a statement in your voice. The total character count MUST be less than 280. No emojis. Use \n\n (double spaces) between statements.
"""


class GaladrielAgent:
    agent: AgentConfig

    perplexity_client: PerplexityClient
    galadriel_client: GaladrielClient
    twitter_client: TwitterClient

    post_interval_minutes_min: int
    post_interval_minutes_max: int

    # pylint: disable=R0917:
    def __init__(
        self,
        api_key: str,
        agent_name: str,
        perplexity_api_key: str,
        twitter_credentials: TwitterCredentials,
        post_interval_minutes_min: int = 90,
        post_interval_minutes_max: int = 180,
    ):
        agent_path = Path("agents") / f"{agent_name}.json"
        with open(agent_path, "r", encoding="utf-8") as f:
            agent_dict = json.loads(f.read())

        init_logging(agent_dict.get("settings", {}).get("debug"))

        missing_fields: List[str] = [
            field
            for field in AgentConfig.required_fields()
            if not agent_dict.get(field)
        ]
        if missing_fields:
            raise KeyError(
                f"Character file is missing required fields: {', '.join(missing_fields)}"
            )
        # TODO: validate types
        self.agent = AgentConfig.from_json(agent_dict)

        self.galadriel_client = GaladrielClient(api_key=api_key)
        self.perplexity_client = PerplexityClient(perplexity_api_key)
        self.twitter_client = TwitterClient(twitter_credentials)

        self.post_interval_minutes_min = post_interval_minutes_min
        self.post_interval_minutes_max = post_interval_minutes_max

    async def run(self):
        logger.info("Running agent!")

        while True:
            # TODO: need to check last tweet time and schedule sleep accordingly
            await self._post_tweet()
            sleep_time = random.randint(
                self.post_interval_minutes_min,
                self.post_interval_minutes_max,
            )
            logger.info(f"Next Tweet scheduled in {sleep_time} minutes.")
            await asyncio.sleep(sleep_time * 60)

    async def _post_tweet(self):
        prompt = await self._format_prompt()
        messages = [
            {"role": "system", "content": self.agent.system},
            {"role": "user", "content": prompt},
        ]
        response = await self.galadriel_client.completion(
            self.agent.settings.get("model", "gpt-4o"), messages
        )
        if response and response.choices and response.choices[0].message:
            message = response.choices[0].message.content
            response = await self.twitter_client.post_tweet(message)
            if tweet_id := (response and response.get("data", {}).get("id")):
                logger.debug(f"Tweet ID: {tweet_id}")
                # TODO: save topic, so we could exclude it for next tweets
        else:
            logger.error(
                f"Unexpected API response from Galadriel: \n{response.to_json()}"
            )

    async def _format_prompt(self) -> str:
        # TODO: need to update prompt etc etc
        data = {
            # TODO: knowledge?
            "knowledge": "\n".join(self.agent.knowledge[:3]),
            "agent_name": self.agent.name,
            "twitter_user_name": self.agent.extra_fields.get("twitter_profile", {}).get(
                "username", "user"
            ),
            "bio": self._get_formatted_bio(),
            "lore": self._get_formatted_lore(),
            # TODO: is topics needed, also check that its not a recently used topic
            "topics": self._get_formatted_topics(),
            "post_directions": self._get_formatted_post_directions(),
        }

        perplexity_result = await self.perplexity_client.search_topic(
            random.choice(self.agent.search_queries)
        )
        if perplexity_result:
            data["perplexity_content"] = perplexity_result.content
            data["perplexity_sources"] = perplexity_result.sources
        else:
            # What to do if perplexity call fails?
            data["perplexity_content"] = ""
            data["perplexity_sources"] = ""

        prompt = PROMPT_TEMPLATE
        for k, v in data.items():
            prompt = prompt.replace("{{" + k + "}}", v)
        logger.debug(f"Got full formatted prompt: \n{prompt}")
        return prompt

    def _get_formatted_bio(self) -> str:
        bio = self.agent.bio
        return " ".join(random.sample(bio, min(len(bio), 3)))

    def _get_formatted_lore(self) -> str:
        lore = self.agent.lore
        shuffled_lore = random.sample(lore, len(lore))
        selected_lore = shuffled_lore[:10]
        return "\n".join(selected_lore)

    def _get_formatted_topics(self) -> str:
        topics = self.agent.topics
        shuffled_topics = random.sample(topics, len(topics))

        selected_topics = shuffled_topics[:5]

        formatted_topics = ""
        for index, topic in enumerate(selected_topics):
            if index == len(selected_topics) - 2:
                formatted_topics += topic + " and "
            elif index == len(selected_topics) - 1:
                formatted_topics += topic
            else:
                formatted_topics += topic + ", "
        return f"{self.agent.name} is interested in {formatted_topics}"

    def _get_formatted_post_directions(self) -> str:
        style = self.agent.style
        merged_styles = "\n".join(style.get("all", []) + style.get("post", []))
        return self._add_header(
            f"# Post Directions for {self.agent.name}", merged_styles
        )

    def _add_header(self, header: str, body: str) -> str:
        if not body:
            return ""
        full_header = ""
        if header:
            full_header = header + "\n"
        return f"{full_header}{body}\n"
