from enum import IntEnum


class ErrorCodes(IntEnum):
    CANT_READ_TLS = 0
    BAD_USER_AGENT = 100
    BAD_JSON = 101
    TOOL_ALREADY_EXISTS = 200
    EMPTY_TOKEN = 300
    BAD_TOKEN = 301
    EXPIRED_TOKEN = 302
    NOT_FOUND = 404

