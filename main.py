import asyncio
import os
import argparse
from pathlib import Path

from dotenv import load_dotenv

from galadriel_agent.agent import GaladrielAgent
from galadriel_agent.clients.twitter import TwitterCredentials


def _load_dotenv():
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, help="Name of the agent to run")
    args = parser.parse_args()

    _load_dotenv()
    twitter_credentials = TwitterCredentials(
        consumer_api_key=os.getenv("TWITTER_CONSUMER_API_KEY"),
        consumer_api_secret=os.getenv("TWITTER_CONSUMER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )
    agent = GaladrielAgent(
        api_key=os.getenv("GALADRIEL_API_KEY"),
        agent_name=args.agent,
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
        twitter_credentials=twitter_credentials,
    )
    asyncio.run(agent.run())
