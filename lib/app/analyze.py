from . import BaseApi
from fastapi import Request
from fastapi.responses import JSONResponse
from lib.db.tables import Fingerprint
import json


class Analyze(BaseApi):
    def init_api(self):
        self.add_route("/all", self.all, "get")

    async def all(self, request: Request):
        tls = json.loads(request.headers.get("x-tls", "{}"))
        ja3_hash = tls["ja3_hash"] if tls else "failed to generate"
        ja3_text = tls["ja3_text"] if tls else "failed to generate"
        fp = Fingerprint.get_or_none(hash=ja3_hash)
        if fp:
            tools = [{
                "kind": it.kind_attr.name,
                "tool": it.as_str
            } for it in fp.tools]
        else:
            tools = []
        user_agent = request.headers.get("User-Agent", "undefined")

        json_response = {
            "ja3_text": ja3_text,
            "ja3_hash": ja3_hash,
            "user_agent": user_agent,
            "tools": tools
        }
        return JSONResponse(json_response)
