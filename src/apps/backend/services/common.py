import base64
import json
import re
import httpagentparser
import hashlib
from django.http import JsonResponse, HttpRequest
from rest_framework import status
from src.apps.backend.models import Fingerprint, Tool
from . import TLSParser, ErrorCodes


def success(**data) -> JsonResponse:
    """
    Build a success response
    :param data: arguments to the body
    :return: JsonResponse object
    """
    return JsonResponse({
        "success": True,
        "data": data
    }, status=status.HTTP_200_OK)


def server_error(code: ErrorCodes, message="Internal server error") -> JsonResponse:
    """
    Build a server error response
    :param code: own app error code (services.ErrorCodes)
    :param message: message will be added to body
    :return: JsonResponse object
    """
    return _error_response(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR)


def client_error(code: ErrorCodes, message="Bad request") -> JsonResponse:
    """
    Build a client error response
    :param code: own client error code (services.ErrorCodes)
    :param message: message will be added to body
    :return: JsonResponse object
    """
    return _error_response(message, code, status.HTTP_400_BAD_REQUEST)


def get_headers(request: HttpRequest, *headers) -> list[str]:
    """
    Safe get all listed headers
    :param request: request object
    :param headers: name of headers to be returned
    :return: values of listed headers
    """
    return [request.headers.get(header) for header in headers]


def dig(obj: [list, tuple, dict], *args) -> [None, int, str, list, tuple, dict]:
    """
    Safe navigate on json-serialized object
    :param obj: json-serialized object
    :param args: path to the endpoint
    :return: value of endpoint
    """
    try:
        for arg in args:
            obj = obj[arg]
        return obj
    except (KeyError, IndexError, TypeError):
        return


def get_tls_fp(request: HttpRequest) -> [None, dict]:
    """
    Extract tls fingerprint
    :param request: request object
    :return: dictionary with tls fingerprint
    """
    client_hello, = get_headers(request, "X-Client-Hello")
    if not client_hello:
        return
    try:
        return TLSParser(base64.b64decode(client_hello)).as_dict()
    except ValueError:
        return


def get_tools(tls_fp: dict) -> list[dict]:
    """
    Find tools with the given fingerprint
    :param tls_fp: generated tls fingerprint
    :return: list of tools
    """
    fp = Fingerprint.objects.filter(hash=tls_fp["ja3_hash"], kind=Fingerprint.Kind.JA3).first() or \
         Fingerprint.objects.filter(hash=tls_fp["ja3n_hash"], kind=Fingerprint.Kind.JA3N).first()

    return [{"kind": Tool.Kind(item.kind).name, "tool": str(item)} for item in (fp.tools.all() if fp else [])]


def get_or_create_tls_fp(tls_fp: dict) -> Fingerprint:
    """
    Get TLS fp or create if doesn't exist
    :param tls_fp: generated tls fingerprint
    :return: Fingerprint object
    """
    return Fingerprint.objects.filter(hash=tls_fp["ja3_hash"], kind=Fingerprint.Kind.JA3).first() or \
           Fingerprint.objects.get_or_create(hash=tls_fp["ja3n_hash"], kind=Fingerprint.Kind.JA3N,
                                             defaults={"value": tls_fp["ja3n_text"]})


def get_or_create_webgl_fp(webgl_hash: str, webgl_raw: str) -> Fingerprint:
    """
    Get WEBGL fp or create if doesn't exist
    :param webgl_hash: hash of webgl data
    :param webgl_raw: raw webgl data
    :return: Fingerprint object
    """
    webgl_fingerprint, _ = Fingerprint.objects.get_or_create(
        hash=webgl_hash,
        kind=Fingerprint.Kind.WEBGL,
        defaults={"value": webgl_raw}
    )
    return webgl_fingerprint


def get_ua_info(user_agent: str) -> list[[bool, str, None]]:
    """
    Parse data from user agent
    :param user_agent: User-Agent header
    :return: list of parsed user-agents elements
    """
    if not user_agent:
        return [False] + [None] * 4
    ua = httpagentparser.detect(user_agent)

    platform_name    = dig(ua, "platform", "name")
    platform_version = dig(ua, "platform", "version")
    browser_name     = dig(ua, "browser", "name")
    browser_version  = dig(ua, "browser", "version")

    valid = platform_name in _PLATFORMS and browser_name in _BROWSERS

    return [valid, platform_name, platform_version, browser_name, browser_version]


def params_for_client(browser_name: str, tls_fp: dict) -> list[[str, int]]:
    """
    List of params matched by browser name
    :param browser_name: browser
    :param tls_fp: tls fingerprint
    :return: list of params
    """
    if re.search(r'bot', browser_name, re.I):
        return [Tool.Kind.SEARCH_BOT, Fingerprint.Kind.JA3, tls_fp["ja3_hash"], tls_fp["ja3_text"]]
    else:
        return [Tool.Kind.BROWSER, Fingerprint.Kind.JA3N, tls_fp["ja3n_hash"], tls_fp["ja3n_text"]]


def create_fp(fp_kind: Fingerprint.Kind, ja3_hash: str, ja3_text: str) -> list[Fingerprint, bool]:
    """
    Create model Fingerprint
    :param fp_kind: kind of Fingerprint
    :param ja3_hash: given hash (ja3 or ja3n)
    :param ja3_text: given full value of fp
    :return: Fingerprint object
    """
    return Fingerprint.objects.get_or_create(
        hash=ja3_hash,
        kind=fp_kind,
        defaults={"value": ja3_text}
    )


def create_tool(browser_name: str, browser_version: str,
                platform_name: str, platform_version: str,
                tool_kind: str) -> list[Tool, bool]:
    """
    Create Tool object
    :param browser_name: name of browser
    :param browser_version: version of browser
    :param platform_name: name of platform
    :param platform_version: version of platform
    :param tool_kind: kind of Tool
    :return: Tool object
    """
    platform_name += " " + platform_version if platform_version else ""
    return Tool.objects.get_or_create(
        name=browser_name,
        system=platform_name,
        version=browser_version,
        kind=tool_kind
    )


def add_fp_to_tool(fp: Fingerprint, tool: Tool) -> bool:
    """
    Add fingerprint to tool if tool don't have it
    :param fp: Fingerprint object
    :param tool: Tool object
    :return: added or not
    """
    fp_of_parsed_tool = tool.fingerprints.all()
    if fp not in fp_of_parsed_tool:
        tool.fingerprints.add(fp)
        return True
    else:
        return False


def _error_response(message: str, code: ErrorCodes, status_code: int) -> JsonResponse:
    """
    Build error response
    :param code: own error code (services.ErrorCodes)
    :param message: message will be added to body
    :param status_code: HTTP status code
    :return: JsonResponse object
    """
    return JsonResponse({
        "success": False,
        "error": {
            "message": message,
            "code": code,
        }
    }, status=status_code)


def webgl_is_valid(webgl_hash: str, webgl_raw: str) -> bool:
    """
    Validate webgl
    :param webgl_hash: sha256 hash of webgl
    :param webgl_raw: base64 encoded webgl
    :return: valid or not
    """
    if not (webgl_hash and webgl_raw):
        return False

    try:
        webgl_raw_decoded_hash = hashlib.sha256(webgl_raw.encode("utf-8")).hexdigest()
    except ValueError:
        return False

    if webgl_raw_decoded_hash != webgl_hash:
        return False

    try:
        webgl_obj = json.loads(webgl_raw)
    except json.JSONDecoder:
        return False

    if not webgl_obj:
        return False

    return True


AUTOMATION_KEYS = ["webdriver_detected", "window_automations_detected",
                   "document_automations_detected", "cdc_detected"]


_WEBGL_KEYS = ['VERSION', 'SHADING_LANGUAGE_VERSION', 'VENDOR', 'RENDERER', 'MAX_VERTEX_ATTRIBS',
               'MAX_VERTEX_UNIFORM_VECTORS', 'MAX_VERTEX_TEXTURE_IMAGE_UNITS', 'MAX_VARYING_VECTORS',
               'MAX_VERTEX_UNIFORM_COMPONENTS', 'MAX_VERTEX_UNIFORM_BLOCKS', 'MAX_VERTEX_OUTPUT_COMPONENTS',
               'MAX_VARYING_COMPONENTS', 'MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS',
               'MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS', 'MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS',
               'ALIASED_LINE_WIDTH_RANGE', 'ALIASED_POINT_SIZE_RANGE', 'MAX_FRAGMENT_UNIFORM_VECTORS',
               'MAX_TEXTURE_IMAGE_UNITS', 'MAX_FRAGMENT_UNIFORM_COMPONENTS', 'MAX_FRAGMENT_UNIFORM_BLOCKS',
               'MAX_FRAGMENT_INPUT_COMPONENTS', 'MIN_PROGRAM_TEXEL_OFFSET', 'MAX_PROGRAM_TEXEL_OFFSET',
               'MAX_DRAW_BUFFERS', 'MAX_COLOR_ATTACHMENTS', 'MAX_SAMPLES', 'MAX_RENDERBUFFER_SIZE',
               'MAX_VIEWPORT_DIMS', 'RED_BITS', 'GREEN_BITS', 'BLUE_BITS', 'ALPHA_BITS', 'DEPTH_BITS',
               'STENCIL_BITS', 'MAX_TEXTURE_SIZE', 'MAX_CUBE_MAP_TEXTURE_SIZE',
               'MAX_COMBINED_TEXTURE_IMAGE_UNITS', 'MAX_3D_TEXTURE_SIZE', 'MAX_ARRAY_TEXTURE_LAYERS',
               'MAX_TEXTURE_LOD_BIAS', 'MAX_UNIFORM_BUFFER_BINDINGS', 'MAX_UNIFORM_BLOCK_SIZE',
               'UNIFORM_BUFFER_OFFSET_ALIGNMENT', 'MAX_COMBINED_UNIFORM_BLOCKS',
               'MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS', 'MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS']


_PLATFORMS = ['Android', 'PlayStation', 'Nokia S40',
              'Symbian', 'Mac OS', 'BlackBerry',
              'Linux', ' ChromeOS', 'Windows', 'iOS']


_BROWSERS = ['AndroidBrowser', 'ArchiveDotOrgBot', 'BaiduBot',
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
