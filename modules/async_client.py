# From Splatbot: https://github.com/ktraw2/SplatBot/blob/master/modules/async_client.py

import aiohttp
import asyncio
import json


class AsyncClient:
    def __init__(self, header: str = "", request_prefix: str = "", request_suffix: str = "", session=None):
        self.header = header
        self.request_prefix = request_prefix
        self.request_suffix = request_suffix
        self.connection = session

    async def send_request(self, request: str):
        async with self.connection.get(self.request_prefix + request + self.request_suffix, headers=self.header) as response:
            if response.status == 200:
                return await response.text()
            elif response.status == 429:
                # bot is sending too many requests, try again after a couple seconds
                print("Bot is being rate limited, resending request...")
                await asyncio.sleep(5)
                return await self.send_request(request)
            else:
                return '{"error":' + str(response.status) + '}'

    async def send_image_request(self, image_url: str, file_path: str):
        async with self.connection.get(image_url, headers=self.header) as response:
            image = await response.read()
            if response.status == 200:
                with open(file_path, "wb") as f:
                    f.write(image)
                    return
            elif response.status == 429:
                # bot is sending too many requests, try again after a couple seconds
                print("Bot is being rate limited, resending request...")
                await asyncio.sleep(5)
                return await self.send_image_request(image_url, file_path)
            else:
                return '{"error":' + str(response.status) + '}'

    async def send_json_request(self, request: str, return_raw_and_json: bool = False):
        raw_data = await self.send_request(request)
        json_data = json.loads(raw_data)
        if return_raw_and_json:
            return json_data, raw_data
        else:
            return json_data
