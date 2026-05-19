from http import HTTPStatus
from typing import Type

from pydantic import ValidationError

from src.core.common.error_messages import (
    QUOTA_EXCEEDED,
    RATE_LIMIT_EXCEEDED,
    VALIDATE_ERROR,
)
from src.core.common.types import ResponseBundle, ScopusModel
from src.core.config.config import LOG
from src.core.data.enums import ScopusCode
from src.core.data.serializers import (
    ScopusAbstract,
    ScopusError,
    ScopusHeaders,
    ScopusSearch,
)
from src.core.domain.http_exceptions import InternalError, ScopusAPIError


class ScopusResponse:
    """Handle errors and status from Scopus responses"""

    @classmethod
    def _validate(
        cls, model: Type[ScopusModel], response: ResponseBundle
    ) -> ScopusModel:
        try:
            if response.code >= HTTPStatus.BAD_REQUEST:
                quota = ScopusHeaders.model_validate(response.headers)
                LOG.quota(quota, response.code)

                if response.code == HTTPStatus.TOO_MANY_REQUESTS:
                    error_response = ScopusError.model_validate(response.data)

                    if error_response.code == ScopusCode.QUOTA:
                        LOG.error(QUOTA_EXCEEDED)
                        LOG.info(
                            "Please try again on \033[33m"
                            f"{quota.reset_datetime}\033[m"
                        )

                    elif error_response.code == ScopusCode.RATE_LIMIT:
                        LOG.error(RATE_LIMIT_EXCEEDED)

                raise ScopusAPIError(
                    quota.status,
                    response.code,
                    response.data,
                    quota.model_dump(),
                )

            return model.model_validate(response.data)

        except (ValidationError, KeyError) as exc:
            raise InternalError(VALIDATE_ERROR, exc) from exc

    @classmethod
    def validate_search(cls, response: ResponseBundle) -> ScopusSearch:
        return cls._validate(ScopusSearch, response)

    @classmethod
    def validate_abstract(cls, response: ResponseBundle) -> ScopusAbstract:
        return cls._validate(ScopusAbstract, response)
