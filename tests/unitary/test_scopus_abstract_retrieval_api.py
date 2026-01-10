from asyncio import CancelledError
from unittest.mock import AsyncMock, MagicMock

from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.error_messages import CANCELLED_ERROR, QUOTA_EXCEEDED
from src.core.data.enums import Column
from src.core.data.survey_details import SurveyDetails
from src.core.domain.http_exceptions import ServiceUnavailable, TooManyRequests
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn, results_mock
from tests.mocks.raw import (
    API_KEY,
    HTTP_429,
    HTTP_503,
    LOG_NO_QUOTA,
    LOG_ONE_QUOTA,
    LOG_QUOTA,
)
from tests.mocks.unitary import (
    ONE_ABSTRACT,
    ONE_ABSTRACT_AUTHORS,
    ONE_ABSTRACT_FULL,
)

SURVEY_DETAILS = MagicMock(spec=SurveyDetails, abstract_quota=LOG_QUOTA)
ABSTRACT_API = ScopusAbstractRetrievalAPI(
    AsyncMock(spec=HTTPClient),
    MagicMock(spec=URLBuilder),
    SURVEY_DETAILS,
)
VALIDATE_ABSTRACT = fqn(ScopusResponse.validate_abstract)
STEP = fqn(ProgressBar.step)


@mark.asyncio
async def test_retrieve_one_partial_abstract(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(1))
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author"


@mark.asyncio
async def test_retrieve_one_abstract_authors(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT_AUTHORS)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(1))
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author_1, any_author_2"


@mark.asyncio
async def test_retrieve_one_abstract_full(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT_FULL)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(1))
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result["Abstract"].iloc[0] == "any_abstract"


@mark.asyncio
async def test_retrieve_two_abstracts(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(2))
    assert result.shape == (2, 11) and mock.call_count == 2


@mark.asyncio
async def test_retrieve_more_abstracts(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(7))
    assert result.shape == (7, 11) and mock.call_count == 7


@mark.asyncio
async def test_retrieve_one_last_quota(mocker: Mocker):
    SURVEY_DETAILS.abstract_quota = LOG_ONE_QUOTA
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(7))
    assert result.shape == (2, 11) and mock.call_count == 2


@mark.asyncio
async def test_retrieve_no_remaining_quota(mocker: Mocker):
    SURVEY_DETAILS.abstract_quota = LOG_NO_QUOTA
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(1))
    assert result.shape == (1, 11) and mock.call_count == 1


@mark.asyncio
async def test_retrieve_quota_exceeded(mocker: Mocker):
    SURVEY_DETAILS.abstract_quota = LOG_NO_QUOTA
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    with raises(TooManyRequests) as info:
        await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(7))
    assert_http_error(info, HTTP_429, QUOTA_EXCEEDED)
    assert mock.call_count == 1


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker):
    SURVEY_DETAILS.abstract_quota = LOG_QUOTA
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    with raises(ServiceUnavailable) as info:
        await ABSTRACT_API.retrieve_abstracts(API_KEY, results_mock(7))
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert mock.call_count == 4
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
