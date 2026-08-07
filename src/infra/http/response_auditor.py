from http import HTTPStatus

from pydantic import BaseModel, ValidationError

from src.adapters.serializers.scopus_data import (
    ScopusAbstract,
    ScopusError,
    ScopusHeaders,
    ScopusPage,
)
from src.adapters.types import ResponseBundle
from src.core.domain.types import ExcMsg
from src.infra.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from src.infra.exceptions import APIResponseError, APIValidationError
from src.infra.types import APIName
from src.infra.utils import logger


def _validate[T: BaseModel](
    model: type[T], res: ResponseBundle, api_name: APIName
) -> T:
    try:
        if res.code >= HTTPStatus.BAD_REQUEST:
            quota = ScopusHeaders.model_validate(res.headers)

            logger.quota(quota, api_name)
            error_res = ScopusError.model_validate(res.data)

            if res.code == HTTPStatus.TOO_MANY_REQUESTS:

                if error_res.code == QUOTA_ERROR_CODE:
                    logger.error(ExcMsg.QUOTA_EXCEEDED)
                    logger.try_again(quota.reset_datetime)

                elif error_res.code == RATE_LIMIT_ERROR_CODE:
                    logger.error(ExcMsg.RATE_LIMIT_EXCEEDED)

            raise APIResponseError(
                res.code,
                quota.model_dump(),
                error_res.model_dump(),
            )

        return model.model_validate(res.data)

    except ValidationError as exc:
        raise APIValidationError(ExcMsg.VALIDATE_ERROR, exc) from exc


def validate_search_response(res: ResponseBundle) -> ScopusPage:
    return _validate(ScopusPage, res, "search")


def validate_abstract_response(res: ResponseBundle) -> ScopusAbstract:
    return _validate(ScopusAbstract, res, "abstract")
