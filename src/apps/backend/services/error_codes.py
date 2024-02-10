from enum import IntEnum


class ErrorCodes(IntEnum):
    CANT_READ_TLS = 0
    BAD_USER_AGENT = 100
    TOOL_ALREADY_EXISTS = 200
