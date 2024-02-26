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
    @staticmethod
    def search_articles(
        data: GatewaySearch.ParamsType,
    ) -> GatewaySearch.SearchType:
        headers = ApiHeaders(apikey=data.api_key).model_dump(by_alias=True)
        query = quote_plus(' AND '.join(data.keywords))

        url = ApiConfig.get_search_articles_url(query)
        response = HttpHelper.make_request(url, headers)

        if response.status_code != 200:
            message = 'Invalid Response from Scopus API'
            status_phrase = HTTPStatus(response.status_code).phrase

            status = f'{response.status_code} - {status_phrase}'
            detail = ApiConfig.RESPONSES.get(response.status_code, 'null')

            raise ScopusApiError(message, status, detail)

        try:
            content: dict = loads(response.text.encode('UTF-8'))
            if content is None or len(content) == 0:
                raise FailedDependency('Invalid Response from Scopus API')

        except JSONDecodeError as exc:
            message = 'Error in decoding response from Scopus API'
            raise InternalError(message) from exc

        total_results = content['search-results']['opensearch:totalResults']
        if int(total_results) == 0:
            raise NotFound('None articles has been found')

        Logger.info(f'\033[93mTotal Articles Found: {total_results}\033[m')

        return content['search-results']['entry']

    @staticmethod
    def scraping_article(scopus_id: str) -> GatewayScraping.ScrapType:
        headers = PageHeaders().model_dump(by_alias=True)
        url = ApiConfig.get_article_page_url(scopus_id.split(':')[1])
        response = HttpHelper.make_request(url, headers)

        if response.status_code != 200 or not response.text:
            raise FailedDependency('Invalid Response from Article Page')

        return url, response.text
