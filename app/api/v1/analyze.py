import base64
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api import BaseApi
from app.db.tables import Fingerprint
from app.lib.parsers.tls import TLSParser


class Analyze(BaseApi):
    FALLBACK_JA3_FP = {
        "ja3_hash": "failed to generate",
        "ja3_text": "failed to generate",
        "ja3n_hash": "failed to generate",
        "ja3n_text": "failed to generate",
        "tools": []
    }

    def init_api(self, app):
        self.add_route("/all", self.all, "get")

    async def all(self, request: Request):
        client_hello = request.headers.get("X-Client-Hello")
        if not client_hello:
            response = self.FALLBACK_JA3_FP
            response["user_agent"] = request.headers.get("User-Agent", "undefined")
            return JSONResponse(response)

        try:
            response = TLSParser(base64.b64decode(client_hello)).as_json()
            fp = \
                Fingerprint.get_or_none(hash=response["ja3_hash"], kind=Fingerprint.Kind.JA3.value) or \
                Fingerprint.get_or_none(hash=response["ja3n_hash"], kind=Fingerprint.Kind.JA3N.value)

            if fp:
                response["tools"] = [{
                    "kind": it.kind_attr.name,
                    "tool": it.as_str
                } for it in fp.tools]
            else:
                response["tools"] = []

        except ValueError:
            response = self.FALLBACK_JA3_FP

        response["user_agent"] = request.headers.get("User-Agent", "undefined")
        return JSONResponse(response)
