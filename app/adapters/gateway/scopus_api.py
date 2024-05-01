from urllib.parse import quote_plus

from app.adapters.gateway.api_config import ApiConfig
from app.adapters.helpers.http_helper import HttpHelper
from app.core.config import LOG
from app.core.exceptions import ScopusApiError
from app.core.interfaces import Gateway
from app.core.model import ScopusResponse
from app.framework.exceptions import FailedDependency, InternalError, NotFound


class ScopusApi(Gateway):
    BOOLEAN_OPERATOR = ' AND '

    def __init__(self) -> None:
        self.__start = 0
        self.__headers: dict[str, str] = {}
        self.__query = ''

    def __api_call_request(self) -> ScopusResponse:
        url = ApiConfig.get_search_articles_url(self.__query, self.__start)
        response = HttpHelper().make_request(url, self.__headers, False)

        if response.status_code != 200:
            raise ScopusApiError(response)

        if not response.text:
            raise FailedDependency('Invalid Response from Scopus API')

        try:
            LOG.debug(response.json())

            return ScopusResponse.model_validate(response.json())

        except ValueError as error:
            message = 'Error in decoding response from Scopus API'
            raise InternalError(message) from error

    def search_articles(self, data: Gateway.ParamsType) -> Gateway.SearchType:
        self.__headers = ApiConfig.get_api_headers(data.api_key)
        self.__query = quote_plus(self.BOOLEAN_OPERATOR.join(data.keywords))

        scopus_response = self.__api_call_request()
        total_results = scopus_response.total_results

        if total_results == 0:
            raise NotFound('None articles has been found')

        if total_results > scopus_response.items_per_page:
            LOG.progress(0, total_results)

            for index in range(1, scopus_response.count):
                self.__start = index * scopus_response.items_per_page
                pagination_response = self.__api_call_request()
                scopus_response.entry.extend(pagination_response.entry)

                LOG.progress(self.__start, total_results)

            LOG.progress(total_results, total_results)

        LOG.info(f'Total Articles Found: {total_results}')

        return scopus_response.entry

    @staticmethod
    def scraping_article(scopus_id: str) -> Gateway.ScrapType:
        headers = ApiConfig.PAGE_HEADERS
        url = ApiConfig.get_article_page_url(scopus_id.split(':')[1])

        try:
            response = HttpHelper().make_request(url, headers)

            if not response.text:
                return url, ApiConfig.TEMPLATE

        except FailedDependency as error:

            LOG.error(error.message)

            return url, ApiConfig.TEMPLATE

        return url, response.text
