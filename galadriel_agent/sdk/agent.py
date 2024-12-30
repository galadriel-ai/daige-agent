import json
from pathlib import Path

from galadriel_agent.sdk.logging_utils import get_agent_logger
from galadriel_agent.sdk.logging_utils import init_logging

logger = get_agent_logger()


class GaladrielAgent:
    api_key: str

    def __init__(
        self,
        api_key: str,
        agent_name: str,
    ):
        self.api_key = api_key
        agent_path = Path("agents") / f"{agent_name}.json"
        with open(agent_path, "r", encoding="utf-8") as f:
            agent_dict = json.loads(f.read())

        # TODO: validate agent_dict
        init_logging(agent_dict.get("settings", {}).get("debug"))

    async def run(self):
        logger.debug("Running agent - debug")
        logger.info("Running agent - info")
