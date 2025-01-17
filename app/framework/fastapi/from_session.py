from base64 import b64decode
from json import loads

from itsdangerous import TimestampSigner
from itsdangerous.exc import BadSignature
from starlette.requests import HTTPConnection
from starlette.types import Scope

from app.core.config.config import SECRET_KEY


async def from_session(scope: Scope) -> tuple[str, str]:
    connection = HTTPConnection(scope)
    signer = TimestampSigner(str(SECRET_KEY))

    if "session" in connection.cookies:
        data = connection.cookies["session"].encode("utf-8")
        try:
            data = signer.unsign(data, max_age=None)
            scope["session"] = loads(b64decode(data))

            print(f"from_session: {scope['session']}")
            csrf_token = scope["session"]["csrf_token"]

            return csrf_token, "default"

        except BadSignature:
            scope["session"] = {}

    return "anonymous", "default"
