from http import HTTPStatus
from json import JSONDecodeError, loads
from urllib.parse import quote_plus

from app.core.interfaces import GatewayScraping, GatewaySearch
from app.core.models import ApiHeaders, PageHeaders
from app.exceptions import (
    FailedDependency,
    InternalError,
    NotFound,
    ScopusApiError,
)
from app.utils.logger import Logger

from .api_config import ApiConfig
from .http_helper import HttpHelper


class ScopusApi(GatewaySearch, GatewayScraping):
    BOOLEAN_OPERATOR = ' AND '
    ENCODING = 'utf-8'
    DEFAULT_DETAIL = 'null'
    RESULTS_KEY = 'search-results'
    TOTAL_KEY = 'opensearch:totalResults'
    ENTRY_KEY = 'entry'

    @classmethod
    def search_articles(
        cls,
        data: GatewaySearch.ParamsType,
    ) -> GatewaySearch.SearchType:
        headers = ApiHeaders(apikey=data.api_key).model_dump(by_alias=True)
        query = quote_plus(cls.BOOLEAN_OPERATOR.join(data.keywords))

        url = ApiConfig.get_search_articles_url(query)
        response = HttpHelper().make_request(url, headers, False)

        if response.status_code != 200:
            message = 'Invalid Response from Scopus API'
            status_phrase = HTTPStatus(response.status_code).phrase

            status = f'{response.status_code} - {status_phrase}'
            detail = ApiConfig.RESPONSES.get(
                response.status_code, cls.DEFAULT_DETAIL
            )

            raise ScopusApiError(message, status, detail)

        try:
            content: dict = loads(response.text.encode(cls.ENCODING))
            if not content:
                raise FailedDependency('Invalid Response from Scopus API')

        except JSONDecodeError as error:
            message = 'Error in decoding response from Scopus API'
            raise InternalError(message) from error

        total_results = content[cls.RESULTS_KEY][cls.TOTAL_KEY]
        if int(total_results) == 0:
            raise NotFound('None articles has been found')

        Logger.info(f'Total Articles Found: {total_results}')

        return content[cls.RESULTS_KEY][cls.ENTRY_KEY]

    @staticmethod
    def scraping_article(scopus_id: str) -> GatewayScraping.ScrapType:
        headers = PageHeaders().model_dump(by_alias=True)
        url = ApiConfig.get_article_page_url(scopus_id.split(':')[1])

        try:
            response = HttpHelper().make_request(url, headers)

            if not response.text:
                return url, ApiConfig.TEMPLATE

        except FailedDependency as error:
            Logger.error(error.message)
            return url, ApiConfig.TEMPLATE

        return url, response.text
