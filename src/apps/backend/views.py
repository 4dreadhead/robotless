from django.db.utils import OperationalError
from src.apps.backend.services import ErrorCodes, common


def token(req):
    pass


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
