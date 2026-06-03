from http import HTTPStatus
from typing import Type

from pydantic import ValidationError

from src.core.common.types import ResponseBundle, ScopusModel
from src.core.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from src.core.data.enums import ExcMsg
from src.core.data.serializers import (
    ScopusAbstract,
    ScopusError,
    ScopusHeaders,
    ScopusSearch,
)
from src.core.domain.http_exceptions import InternalError, ScopusAPIError
from src.utils import logger


class ScopusResponse:
    """Handle errors and status from Scopus responses"""

    @classmethod
    def _validate(
        cls, model: Type[ScopusModel], response: ResponseBundle
    ) -> ScopusModel:
        try:
            if response.code >= HTTPStatus.BAD_REQUEST:
                quota = ScopusHeaders.model_validate(response.headers)
                logger.quota(quota, response.code)


                if response.code == HTTPStatus.TOO_MANY_REQUESTS:
                    error_response = ScopusError.model_validate(response.data)

                    if error_response.code == QUOTA_ERROR_CODE:
                        logger.error(ExcMsg.QUOTA_EXCEEDED)
                        logger.try_again(quota.reset_datetime)

                    elif error_response.code == RATE_LIMIT_ERROR_CODE:
                        logger.error(ExcMsg.RATE_LIMIT_EXCEEDED)

                raise ScopusAPIError(
                    quota.status,
                    response.code,
                    response.data,
                    quota.model_dump(),
                )

            return model.model_validate(response.data)

        except (ValidationError, KeyError) as exc:
            raise InternalError(ExcMsg.VALIDATE_ERROR, exc) from exc

    @classmethod
    def validate_search(cls, response: ResponseBundle) -> ScopusSearch:
        return cls._validate(ScopusSearch, response)

    @classmethod
    def validate_abstract(cls, response: ResponseBundle) -> ScopusAbstract:
        return cls._validate(ScopusAbstract, response)
