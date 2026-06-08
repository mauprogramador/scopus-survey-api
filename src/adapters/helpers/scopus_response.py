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
        cls, model: Type[ScopusModel], res: ResponseBundle
    ) -> ScopusModel:
        try:
            if res.code >= HTTPStatus.BAD_REQUEST:
                quota = ScopusHeaders.model_validate(res.headers)
                logger.quota(quota, res.code)

                error_res = ScopusError.model_validate(res.data)

                if res.code == HTTPStatus.TOO_MANY_REQUESTS:

                    if error_res.code == QUOTA_ERROR_CODE:
                        logger.error(ExcMsg.QUOTA_EXCEEDED)
                        logger.try_again(quota.reset_datetime)

                    elif error_res.code == RATE_LIMIT_ERROR_CODE:
                        logger.error(ExcMsg.RATE_LIMIT_EXCEEDED)

                raise ScopusAPIError(
                    res.code,
                    quota.model_dump(),
                    error_res.model_dump(),
                    res.data,
                )

            return model.model_validate(res.data)

        except (ValidationError, KeyError) as exc:
            raise InternalError(ExcMsg.VALIDATE_ERROR, exc) from exc

    @classmethod
    def validate_search(cls, res: ResponseBundle) -> ScopusSearch:
        return cls._validate(ScopusSearch, res)

    @classmethod
    def validate_abstract(cls, res: ResponseBundle) -> ScopusAbstract:
        return cls._validate(ScopusAbstract, res)
