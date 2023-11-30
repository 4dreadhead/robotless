import json
import re
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpagentparser
from lib.db.tables import *
from lib.models import EnumExtended


class HtmlPages:
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

    class Code(EnumExtended):
        OK = 0,
        CANT_RECOGNIZE = 1
        CANT_COLLECT = 2
        ALREADY_EXISTS = 3

    def __init__(self, app):
        self.app = app
        self.templates = Jinja2Templates(directory="templates")

        self.register_handlers()

    def register_handlers(self):
        self.app.get("/analyze", response_class=HTMLResponse)(self.read_analyze)
        self.app.get("/share", response_class=HTMLResponse)(self.read_share)

    async def read_analyze(self, request: Request):
        tls = json.loads(request.headers.get("tls", "{}"))
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

        json_response = json.dumps({
            "ja3_text": ja3_text,
            "ja3_hash": ja3_hash,
            "user_agent": user_agent,
            "tools": tools
        })
        return self.templates.TemplateResponse("analyze.html", {"request": request, "jsonResponse": json_response})

    async def read_share(self, request: Request):
        ua_row = request.headers.get("User-Agent", "undefined")
        ua = httpagentparser.detect(ua_row)

        pf = ua["platform"]
        system = pf["name"] + ("_" + pf["version"] if pf.get("version") else "") if pf.get("name") else None
        name = ua["browser"]["name"] if ua.get("browser") else None
        version = ua["browser"].get("version") if name else None

        if not (system in self.PLATFORMS and name in self.BROWSERS):
            return self.share_response(request, self.Code.CANT_RECOGNIZE, {"User-Agent": ua_row})

        tls = json.loads(request.headers.get("tls", "{}"))
        ja3_hash = tls.get("ja3_hash")
        ja3_text = tls.get("ja3_text")
        kind = Tool.Kind.SEARCH_BOT.value if re.search(r'bot', name, re.I) else Tool.Kind.BROWSER.value

        if not (ja3_hash and ja3_text):
            return self.share_response(request, self.Code.CANT_COLLECT, {"User-Agent": ua_row})

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
                request, self.Code.OK,
                {
                    "JA3-hash": fp.hash,
                    "JA3-text": fp.value,
                    "Tool": parsed_tool.as_str,
                    "User-Agent": ua_row
                }
            )
        else:
            return self.share_response(request, self.Code.ALREADY_EXISTS, {"User-Agent": ua_row})

    def share_response(self, request, code, response):
        response["code"] = code.value
        response["Message"] = code.name
        json_response = json.dumps(response)
        return self.templates.TemplateResponse("share.html", {"request": request, "jsonResponse": json_response})
