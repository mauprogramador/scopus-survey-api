from json import JSONDecodeError, loads
from urllib.parse import quote_plus

from app.adapters.gateway.api_config import ApiConfig
from app.adapters.helpers.http_helper import HttpHelper
from app.core.config import LOG
from app.core.exceptions import ScopusApiError
from app.core.interfaces import Gateway
from app.framework.exceptions import FailedDependency, InternalError, NotFound


class ScopusApi(Gateway):
    BOOLEAN_OPERATOR = ' AND '
    ENCODING = 'utf-8'
    RESULTS_KEY = 'search-results'
    TOTAL_KEY = 'opensearch:totalResults'
    ENTRY_KEY = 'entry'

    def search_articles(self, data: Gateway.ParamsType) -> Gateway.SearchType:
        headers = ApiConfig.get_api_headers(data.api_key)
        query = quote_plus(self.BOOLEAN_OPERATOR.join(data.keywords))

        url = ApiConfig.get_search_articles_url(query)
        response = HttpHelper().make_request(url, headers, False)

        if response.status_code != 200:
            raise ScopusApiError(response)

        try:
            content: dict = loads(response.text.encode(self.ENCODING))

            LOG.debug(content)

            if not content:
                raise FailedDependency('Invalid Response from Scopus API')

        except JSONDecodeError as error:
            message = 'Error in decoding response from Scopus API'
            raise InternalError(message) from error

        total_results = content[self.RESULTS_KEY][self.TOTAL_KEY]

        if int(total_results) == 0:
            raise NotFound('None articles has been found')

        LOG.info(f'Total Articles Found: {total_results}')

        return content[self.RESULTS_KEY][self.ENTRY_KEY]

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
