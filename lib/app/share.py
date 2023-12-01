import json
import re
from fastapi import Request
from fastapi.responses import JSONResponse
import httpagentparser
from lib.app import BaseApi
from lib.db.tables import *
from lib.models import EnumExtended


class Share(BaseApi):
    def init_api(self):
        self.add_route("/all", self.all, "get")

    async def all(self, request: Request):
        ua_row = request.headers.get("User-Agent", "undefined")
        ua = httpagentparser.detect(ua_row)

        pf = ua["platform"]
        pf_name = pf["name"]
        system = pf["name"] + ("_" + pf["version"] if pf.get("version") else "") if pf.get("name") else None
        name = ua["browser"]["name"] if ua.get("browser") else None
        version = ua["browser"].get("version") if name else None

        if not (pf_name in self.PLATFORMS and name in self.BROWSERS):
            return self.share_response({"User-Agent": ua_row}, self.Code.CANT_RECOGNIZE)

        tls = json.loads(request.headers.get("x-tls", "{}"))
        ja3_hash = tls.get("ja3_hash")
        ja3_text = tls.get("ja3_text")
        kind = Tool.Kind.SEARCH_BOT.value if re.search(r'bot', name, re.I) else Tool.Kind.BROWSER.value

        if not (ja3_hash and ja3_text):
            return self.share_response({"User-Agent": ua_row}, self.Code.CANT_COLLECT)

        fp, fp_created = Fingerprint.get_or_create(
            hash=ja3_hash,
            defaults={
                "kind": Fingerprint.Kind.JA3.value,
                "value": ja3_text
            }
        )
        parsed_tool, tool_created = Tool.get_or_create(
            name=name,
            system=system,
            version=version,
            kind=kind
        )
        if tool_created or fp_created:
            parsed_tool.fingerprints.add(fp)
            return self.share_response(
                {
                    "JA3-hash": fp.hash,
                    "JA3-text": fp.value,
                    "Tool": parsed_tool.as_str,
                    "User-Agent": ua_row
                },
                self.Code.OK
            )
        else:
            return self.share_response({"User-Agent": ua_row}, self.Code.ALREADY_EXISTS)

    def share_response(self, response, code):
        response["code"] = code.value
        response["Message"] = code.name
        return JSONResponse(response)

    class Code(EnumExtended):
        OK = 0,
        CANT_RECOGNIZE = 1
        CANT_COLLECT = 2
        ALREADY_EXISTS = 3

    PLATFORMS = ['Android', 'PlayStation', 'Nokia S40',
                 'Symbian', 'Mac OS', 'BlackBerry',
                 'Linux', ' ChromeOS', 'Windows', 'iOS']

    BROWSERS = ['AndroidBrowser', 'ArchiveDotOrgBot', 'BaiduBot',
                'BingBot', 'Browser', 'BrowserNG', 'Chrome',
                'ChromeiOS', 'ChromiumEdge', 'Dolfin', 'DotBot',
                'FacebookExternalHit', 'Firefox', 'Galeon',
                'GoogleAppEngine', 'GoogleApps', 'GoogleBot',
                'GoogleFeedFetcher', 'Jasmine', 'Konqueror',
                'LinkedInBot', 'MAUI', 'MJ12Bot', 'MSEdge',
                'Microsoft Internet Explorer', 'NetFront',
                'Netscape', 'NintendoBrowser', 'NokiaOvi',
                'ObigoInternetBrowser', 'OneBrowser', 'Openwave',
                'Opera', 'Opera Mobile', 'Opera', 'PhantomJS',
                'RogerBot', 'RunscopeRadar', 'Safari', 'SeaMonkey',
                'SensikaBot', 'TelecaBrowser', 'TelegramBot',
                'Microsoft Internet Explorer', 'TweetmemeBot',
                'TwitterBot', 'UCBrowser', 'UPBrowser', 'WOSBrowser',
                'WebshotBot', 'Yandex.Browser', 'YandexBot', 'YesupBot',
                'YoudaoBot', 'YoudaoBotImage']