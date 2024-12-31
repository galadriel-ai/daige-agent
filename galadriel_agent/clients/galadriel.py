from typing import Iterable
from typing import Optional

from openai import AsyncOpenAI

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion

from galadriel_agent.logging_utils import get_agent_logger

logger = get_agent_logger()


class GaladrielClient:
    api_key: str

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            base_url="https://api.galadriel.com/v1/verified", api_key=api_key
        )
        # Configurations?

    async def completion(
        self, model: str, messages: Iterable[ChatCompletionMessageParam]
    ) -> Optional[ChatCompletion]:
        try:
            return await self.client.chat.completions.create(
                model=model, messages=messages
            )
        except Exception as e:
            logger.error("Error calling Galadriel completions API", e)
        return None
