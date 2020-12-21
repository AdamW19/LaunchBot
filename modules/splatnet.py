# From Splatbot: https://github.com/ktraw2/SplatBot/blob/master/modules/splatnet.py

from modules.async_client import AsyncClient


class Splatnet(AsyncClient):
    def __init__(self, header="", request_prefix="", request_suffix="", session=None):
        super(Splatnet, self).__init__(header=header, request_prefix=request_prefix,
                                       request_suffix=request_suffix, session=session)

    async def get_turf(self):
        return (await self.send_json_request("schedules"))['regular']

    async def get_ranked(self):
        return (await self.send_json_request("schedules"))['gachi']

    async def get_league(self):
        return (await self.send_json_request("schedules"))['league']

    async def get_salmon_detail(self):
        return (await self.send_json_request("coop-schedules"))['details']

    async def get_na_splatfest(self):
        return (await self.send_json_request("festivals"))['na']
