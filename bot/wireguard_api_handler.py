
from io import BytesIO
from typing import Any, Callable
import aiohttp
from data import API_HOST


class PeerAlreadyExistsError(Exception):
    pass


class APIHandler:

    def __init__(self):
        self.__host = API_HOST
        self.__url_template = f"http://{self.__host}"

    async def get_peer(self, username: str) -> str:
        resp, session = await self.__make_request(aiohttp.ClientSession.get, method=f"clients/{username}")
        res = await resp.text()
        await session.close()
        return res

    async def create_peer(self, username: str) -> str:
        body = {"username": username}
        resp, session = await self.__make_request(aiohttp.ClientSession.post, method="clients", body=body)
        await session.close()

        HTTP_409_CONFLICT = 409
        if resp.status == HTTP_409_CONFLICT:
            raise PeerAlreadyExistsError
        return resp.headers.get("Location", "")

    async def get_active_peers(self) -> list[str]:
        resp, session = await self.__make_request(aiohttp.ClientSession.get, method="clients")
        res = await resp.json()
        await session.close()
        return res

    async def delete_peer(self, username: str):
        await self.__make_request(aiohttp.ClientSession.delete, method=f"clients/{username}")

    async def __make_request(self,
                                 request_method: Callable,
                                 method: str,
                                 body: dict[str, Any] | None = None
                             ) -> tuple[aiohttp.ClientResponse, aiohttp.ClientSession]:

        url = f"{self.__url_template}/{method}"
        headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'plain/text, application/json'
                }

        async with aiohttp.ClientSession() as session:
            return await request_method(session, url=url, json=body, headers=headers), session
                

if __name__ == '__main__':
    import asyncio
    handler = APIHandler()
    print(asyncio.run(handler.get_active_peers()))

