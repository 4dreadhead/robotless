import datetime
import json

import jwt
from django.db.utils import OperationalError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from src.apps.backend.models import Fingerprint
from src.apps.backend.services import ErrorCodes, common


def tls_info(request):
    try:
        user_agent, = common.get_headers(request, "User-Agent")
        tls_fp = common.get_tls_fp(request)
        if not tls_fp:
            raise ValueError("Can't parse tls fp.")
        return common.success(user_agent=user_agent, tools=common.get_tools(tls_fp), **tls_fp)
    except (ValueError, OperationalError):
        return common.server_error(ErrorCodes.CANT_READ_TLS)


def share_data(request):
    user_agent, = common.get_headers(request, "User-Agent")
    user_agent_valid, platform_name, platform_version, browser_name, browser_version = common.get_ua_info(user_agent)

    if not user_agent_valid:
        return common.client_error(ErrorCodes.BAD_USER_AGENT)

    tls_fp = common.get_tls_fp(request)
    if not tls_fp:
        return common.server_error(ErrorCodes.CANT_READ_TLS)

    tool_kind, fp_kind, ja3_hash, ja3_text = common.params_for_client(browser_name, tls_fp)

    fp, fp_created = common.create_fp(fp_kind, ja3_hash, ja3_text)
    tool, tool_created = common.create_tool(browser_name, browser_version, platform_name, platform_version, tool_kind)

    if common.add_fp_to_tool(fp, tool):
        return common.success(fp_kind=fp_kind, ja3_hash=ja3_hash, ja3_text=ja3_text)
    else:
        return common.client_error(ErrorCodes.TOOL_ALREADY_EXISTS, message="Info already exists")


def initial(request):
    tls_fp = common.get_tls_fp(request)
    if not tls_fp:
        raise ValueError("Can't parse tls fp.")
    request.session['tls_fp'] = tls_fp
    return common.success()


@csrf_exempt
def generate_token(request):
    if request.method != 'POST':
        return common.server_error(ErrorCodes.NOT_FOUND)

    client_info = {}

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return common.client_error(ErrorCodes.BAD_JSON)
    webgl_hash = common.dig(body, "webgl_hash")
    webgl_raw = common.dig(body, "webgl_raw")

    if common.webgl_is_valid(webgl_hash, webgl_raw):
        webgl_fingerprint, _ = Fingerprint.objects.get_or_create(
            hash=webgl_hash,
            kind=Fingerprint.Kind.WEBGL,
            defaults={"value": None}
        )
        webgl_score = webgl_fingerprint.state
        client_info["webgl"] = webgl_hash
    else:
        webgl_score = Fingerprint.State.UNTRUSTED
        client_info["webgl"] = ''

    tls_fp = request.session['tls_fp']

    if tls_fp:
        tls_fingerprint, _ = common.get_or_create_tls_fp(tls_fp)
        tls_score = tls_fingerprint.state
        client_info["tls"] = tls_fingerprint.hash
    else:
        tls_score = Fingerprint.State.UNTRUSTED
        client_info["tls"] = ''

    automation = common.dig(body, "automation")

    try:
        automation_score = 0

        if automation["cdp_detected"]:
            automation_score = Fingerprint.State.UNTRUSTED
            client_info["cdp_open"] = True
        else:
            client_info["cdp_open"] = False

        if any(map(lambda x: automation[x], common.AUTOMATION_KEYS)):
            client_info["autotools"] = True
            automation_score = Fingerprint.State.BLACKLISTED
        else:
            client_info["autotools"] = False

    except (ValueError, KeyError, TypeError):
        automation_score = Fingerprint.State.BLACKLISTED

    final_score = tls_score + webgl_score + automation_score
    client_info["score"] = final_score

    match final_score:
        case 0, 3:
            client_info["conclusion"] = Fingerprint.State.TRUSTED.name
        case 6:
            client_info["conclusion"] = Fingerprint.State.UNTRUSTED.name
        case _:
            client_info["conclusion"] = Fingerprint.State.BLACKLISTED.name

    client_info["session_id"] = request.session.session_key
    client_info["timestamp"] = int(datetime.datetime.now().timestamp() * 1000)

    return common.success(token=jwt.encode(client_info, settings.SECRET_KEY, algorithm='HS256'))


def analyze_token(request):
    if request.method != 'POST':
        return common.server_error(ErrorCodes.NOT_FOUND)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return common.client_error(ErrorCodes.BAD_JSON)

    jwt_token = body.get("token")

    if not jwt_token:
        return common.client_error(ErrorCodes.EMPTY_TOKEN)

    try:
        token_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return common.client_error(ErrorCodes.EMPTY_TOKEN)
    except jwt.InvalidTokenError:
        return common.client_error(ErrorCodes.BAD_TOKEN)

    return common.success(**token_info)
