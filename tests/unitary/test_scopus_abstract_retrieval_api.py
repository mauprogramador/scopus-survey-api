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
from src.core.common.error_messages import CANCELLED_ERROR
from src.core.data.enums import Column
from src.core.data.survey_detail import SurveyDetails
from src.core.domain.http_exceptions import ServiceUnavailable
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import API_KEY, HTTP_503
from tests.mocks.unitary import (
    ENTRIES,
    ONE_ABSTRACT,
    ONE_ABSTRACT_AUTHORS,
    ONE_ABSTRACT_FULL,
)

ABSTRACT_API = ScopusAbstractRetrievalAPI(
    AsyncMock(spec=HTTPClient),
    MagicMock(spec=URLBuilder),
    MagicMock(spec=SurveyDetails),
)
VALIDATE_ABSTRACT = fqn(ScopusResponse.validate_abstract)
STEP = fqn(ProgressBar.step)


@mark.asyncio
async def test_retrieve_one_partial_abstract(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES[:1])
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author"


@mark.asyncio
async def test_retrieve_one_abstract_authors(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT_AUTHORS)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES[:1])
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author_1, any_author_2"


@mark.asyncio
async def test_retrieve_one_abstract_full(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT_FULL)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES[:1])
    assert result.shape == (1, 11) and mock.call_count == 1
    assert result["Abstract"].iloc[0] == "any_abstract"


@mark.asyncio
async def test_retrieve_two_abstract(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES[:2])
    assert result.shape == (2, 11) and mock.call_count == 2


@mark.asyncio
async def test_retrieve_more_abstracts(mocker: Mocker):
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    result = await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES)
    assert result.shape == (7, 11) and mock.call_count == 7


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker):
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    mock = mocker.patch(VALIDATE_ABSTRACT, return_value=ONE_ABSTRACT)
    with raises(ServiceUnavailable) as info:
        await ABSTRACT_API.retrieve_abstracts(API_KEY, ENTRIES)
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert mock.call_count == 3
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
