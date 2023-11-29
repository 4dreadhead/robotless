from . import BaseApi
from fastapi import Request
from fastapi.responses import PlainTextResponse
import json


class Collect(BaseApi):
    def init_api(self):
        self.add_route("/tls", self.tls, "get")
        self.add_route("/akamai", self.akamai, "get")

    async def tls(self, request: Request):
        return PlainTextResponse(content=json.dumps(json.loads(request.headers.get("tls", "{}")), indent=4))

    async def akamai(self, request: Request):
        return PlainTextResponse(content=json.dumps(json.loads(request.headers.get("akamai", "{}")), indent=4))
