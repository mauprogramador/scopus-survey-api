from http import HTTPStatus
from json.decoder import JSONDecodeError

from pydantic import BaseModel
from requests import Response

from app.core.config.config import LOG
from app.core.common.messages import (
    DECODING_ERROR,
    QUOTA_EXCEEDED,
    RATE_LIMIT_EXCEEDED,
    VALIDATE_ERROR,
)
from app.core.config.scopus import (
    QUOTA_EXCEEDED_CODE,
    RATE_LIMIT_EXCEEDED_CODE,
)
from app.core.domain.interfaces import ScopusResponseABC
from app.core.domain.exceptions import ScopusAPIError
from app.core.domain.http_exceptions import BadGateway, InternalError
from app.core.data.serializers import (
    ScopusErrorResponse,
    ScopusQuotaRateLimit,
)


class ScopusResponse(ScopusResponseABC):
    """Handle errors and status from Scopus responses"""

    def __init__(self, model: BaseModel, exc_message: str) -> None:
        """Handle errors and status from Scopus responses"""
        self.__model = model
        self.__exc_message = exc_message

    def handle(self, response: Response) -> BaseModel:
        code, json = response.status_code, response.json()

        try:
            quota = ScopusQuotaRateLimit.model_validate(response.headers)
            LOG.quota(quota, code)

            if code != HTTPStatus.OK:

                if code == HTTPStatus.TOO_MANY_REQUESTS:
                    error_response = ScopusErrorResponse.model_validate(json)

                    if error_response.code == QUOTA_EXCEEDED_CODE:
                        LOG.error(
                            QUOTA_EXCEEDED.format(
                                f"\033[33m{quota.reset_datetime}\033[m"
                            )
                        )

                    if error_response.code == RATE_LIMIT_EXCEEDED_CODE:
                        LOG.error(RATE_LIMIT_EXCEEDED)

                raise ScopusAPIError(
                    code, json, quota.status, self.__exc_message
                )

            if not response.text:
                raise BadGateway(self.__exc_message)

            return self.__model.model_validate(json)

        except JSONDecodeError as error:
            raise InternalError(DECODING_ERROR) from error

        except KeyError as error:
            raise InternalError(VALIDATE_ERROR) from error
