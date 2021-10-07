import aiohttp
import logging

from typing import Optional


_LOGGER = logging.getLogger(__name__)

API_URL = "https://anovaculinary.io/devices/{id}/states/"

class AnovaCooker:
    def __init__(self, device_id: str):
        self.device_id = device_id

        self.max_age = '10s'

    async def _request(self, timeout: int=10) -> list:
        params = {
            'limit': 1,
            'max-age': self.max_age,
        }

        url = API_URL.format(id=self.device_id)

        client_timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            _LOGGER.debug(f"Requesting '{url}'")
            req = session.get(url, params=params)

            async with req as response:
                if 200 != response.status:
                    raise RuntimeError(f'Request failed: {response.status}')

                return await response.json(content_type=None)


    async def update_state(self, timeout: int=10) -> Optional[dict]:
        """
        TODO
        """
        self.state = None

        states = (await self._request(timeout=timeout))

        if states and len(states) > 0:
            self.state = states[0]
            return True

        return False

    @property
    def job_status(self) -> str:
        if not self.state:
            return 'offline'

        return self.state['body']['job-status']['state']

    @property 
    def mode(self) -> str:
        if not self.state:
            return 'offline'

        job = self.state['body']['job']
        if job['mode'] == 'IDLE':
            return 'idle'

        return self.state['body']['job-status']['state'].lower()

    @property
    def time_remaining(self) -> int:
        if not self.state:
            return 0

        return self.state['body']['job-status']['cook-time-remaining']
