import os
from dataclasses import dataclass
from typing import Dict
from typing import Literal
from typing import Optional

from requests_oauthlib import OAuth1Session

from galadriel_agent.logging_utils import get_agent_logger

logger = get_agent_logger()


@dataclass
class TwitterCredentials:
    consumer_api_key: str
    consumer_api_secret: str
    access_token: str
    access_token_secret: str


class TwitterConnectionError(Exception):
    """Base exception for Twitter connection errors"""


class TwitterAPIError(TwitterConnectionError):
    """Raised when Twitter API requests fail"""


class TwitterClient:
    oauth_session: OAuth1Session

    def __init__(self, _credentials: TwitterCredentials):
        # Might want to look into Oauth2Session, has higher limits, but can we POST tweets with it?
        # https://developer.x.com/en/docs/x-api/rate-limits
        self.oauth_session = OAuth1Session(
            _credentials.consumer_api_key,
            client_secret=_credentials.consumer_api_secret,
            resource_owner_key=_credentials.access_token,
            resource_owner_secret=_credentials.access_token_secret,
        )

    async def post_tweet(self, message: str) -> Optional[Dict]:
        if os.getenv("DRY_RUN"):
            logger.info(f"Would have posted tweet: {message}")
            return None
        response = await self._make_request("POST", "tweets", json={"text": message})
        logger.info(f"Tweet posted successfully: {message}")
        return response

    async def _make_request(
        self, method: Literal["GET", "POST"], endpoint: str, **kwargs
    ) -> Dict:
        # TODO: Should be async ideally
        logger.debug(f"Making {method} request to {endpoint}")
        try:
            oauth = self.oauth_session
            full_url = f"https://api.twitter.com/2/{endpoint.lstrip('/')}"

            response = getattr(oauth, method.lower())(full_url, **kwargs)

            if response.status_code not in [200, 201]:
                logger.error(
                    f"Request failed: {response.status_code} - {response.text}"
                )
                raise TwitterAPIError(
                    f"Request failed with status {response.status_code}: {response.text}"
                )

            logger.debug(f"Request successful: {response.status_code}")
            return response.json()

        except Exception as e:
            raise TwitterAPIError(f"API request failed: {str(e)}")
