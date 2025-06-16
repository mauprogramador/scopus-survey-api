from http import HTTPStatus
from json import JSONDecodeError

from pydantic import BaseModel, ValidationError
from requests import Response

from src.core.common.messages import (
    QUOTA_EXCEEDED,
    RATE_LIMIT_EXCEEDED,
    VALIDATE_ERROR,
)
from src.core.config.config import LOG
from src.core.data.enums import ScopusCode
from src.core.data.serializers import ScopusErrorResponse, ScopusQuotaRateLimit
from src.core.domain.http_exceptions import (
    BadGateway,
    InternalError,
    ScopusAPIError,
)
from src.core.domain.interfaces import ScopusResponseABC


class ScopusResponse(ScopusResponseABC):
    """Handle errors and status from Scopus responses"""

    def __init__(self, model: BaseModel, exc_message: str) -> None:
        """Handle errors and status from Scopus responses"""
        self.__model = model
        self.__exc_message = exc_message

    def validate(self, response: Response) -> BaseModel:
        code, json = response.status_code, response.json()
        print(json)

        try:
            quota = ScopusQuotaRateLimit.model_validate(response.headers)
            LOG.quota(quota, code)

            if code != HTTPStatus.OK:

                if code == HTTPStatus.TOO_MANY_REQUESTS:
                    error_response = ScopusErrorResponse.model_validate(json)

                    if error_response.code == ScopusCode.QUOTA:
                        LOG.error(QUOTA_EXCEEDED)
                        LOG.info(
                            "Please try again on \033[33m"
                            f"{quota.reset_datetime}\033[m"
                        )

                    if error_response.code == ScopusCode.RATE_LIMIT:
                        LOG.error(RATE_LIMIT_EXCEEDED)

                raise ScopusAPIError(code, json, quota.status)

            if not response.text:
                raise BadGateway(self.__exc_message)

            return self.__model.model_validate(json)

        except (ValidationError, JSONDecodeError, KeyError) as exc:
            raise InternalError(VALIDATE_ERROR, exc) from exc
