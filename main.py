import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from galadriel_agent.sdk.agent import GaladrielAgent

if __name__ == "__main__":
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)
    agent = GaladrielAgent(
        api_key=os.getenv("GALADRIEL_API_KEY"),
        agent_name="daige",
    )
    asyncio.run(agent.run())
