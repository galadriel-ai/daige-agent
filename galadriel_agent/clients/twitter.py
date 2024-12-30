from galadriel_agent.logging_utils import get_agent_logger

logger = get_agent_logger()


class TwitterClient:

    def __init__(self):
        # TODO:
        pass

    async def post_tweet(self, content: str) -> bool:
        logger.info(f"Would have posted tweet: {content}")
        return True
