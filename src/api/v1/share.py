import base64
import re
import httpagentparser
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from src.apps.backend.models import Fingerprint, Tool
from src.lib.parsers import TLSParser


class APIShareView(APIView):
    def get(self, request):
        ua_row = request.headers.get("User-Agent", "undefined")
        ua = httpagentparser.detect(ua_row)

        pf = ua["platform"]
        pf_name = pf["name"]
        system = pf["name"] + ("_" + pf["version"] if pf.get("version") else "") if pf.get("name") else None
        name = ua["browser"]["name"] if ua.get("browser") else None
        version = ua["browser"].get("version") if name else None

        if not (pf_name in self.PLATFORMS and name in self.BROWSERS):
            return JsonResponse({"User-Agent": ua_row, "message": "can't recognise"}, status=status.HTTP_400_BAD_REQUEST)

        client_hello = request.headers.get("X-Client-Hello")

        if not client_hello:
            return JsonResponse({"User-Agent": ua_row, "message": "can't collect"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ja3_full = TLSParser(base64.b64decode(client_hello)).as_json()
        except ValueError:
            return JsonResponse({"User-Agent": ua_row, "message": "can't collect"}, status=status.HTTP_400_BAD_REQUEST)

        if re.search(r'bot', name, re.I):
            tool_kind = Tool.Kind.SEARCH_BOT.value
            fp_kind = Fingerprint.Kind.JA3.value
            ja3_hash = ja3_full["ja3_hash"]
            ja3_text = ja3_full["ja3_text"]
        else:
            tool_kind = Tool.Kind.BROWSER.value
            fp_kind = Fingerprint.Kind.JA3N.value
            ja3_hash = ja3_full["ja3n_hash"]
            ja3_text = ja3_full["ja3n_text"]

        fp, fp_created = Fingerprint.objects.get_or_create(
            hash=ja3_hash,
            kind=fp_kind,
            defaults={
                "value": ja3_text
            }
        )
        parsed_tool, tool_created = Tool.objects.get_or_create(
            name=name,
            system=system,
            version=version,
            kind=tool_kind
        )
        fp_of_parsed_tools = parsed_tool.fingerprints.all()
        if fp not in fp_of_parsed_tools:
            parsed_tool.fingerprints.add(fp)
            return JsonResponse(
                {
                    "JA3-type": Fingerprint.Kind(fp.kind).name,
                    "JA3-hash": fp.hash,
                    "JA3-text": fp.value,
                    "Tool": parsed_tool.as_str,
                    "User-Agent": ua_row
                },
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse({"User-Agent": ua_row, "message": "already exists"}, status=status.HTTP_200_OK)


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
