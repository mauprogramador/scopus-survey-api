from typing import Annotated

from fastapi import Query

from app.core.config.config import LOG
from app.core.common.patterns import API_KEY_PATTERN, KEYWORD_PATTERN
from app.core.interfaces import ApiParams
from app.framework.exceptions import Forbidden, UnprocessableContent


class QueryParams(ApiParams):
    API_KEY_QUERY = Query(
        alias='apikey',
        description='Your Scopus API Key',
        min_length=32,
        max_length=32,
        pattern=API_KEY_PATTERN,
    )
    KEYWORDS_QUERY = Query(
        alias='keywords',
        description='Keywords to search for in the articles',
        min_length=1,
        max_length=6,
    )

    def __init__(
        self,
        api_key: Annotated[str | None, API_KEY_QUERY] = None,
        keywords: Annotated[list[str] | None, KEYWORDS_QUERY] = None,
    ) -> None:
        super().__init__()

        if not api_key:
            raise Forbidden('Missing ApiKey required query parameter')

        self.api_key = api_key

        LOG.debug({'api_key': self.api_key})

        if not keywords or not any(keywords):
            raise UnprocessableContent(
                'Missing keywords required query parameter'
            )

        if len(keywords) == 1:
            keywords = keywords[0].split(',')

        self.keywords = list(filter(self.__filter, keywords))

        LOG.debug({'Keywords': self.keywords})

        if len(self.keywords) < 2:
            raise UnprocessableContent('There must be at least two keywords')

    def __filter(self, keyword: str):
        keyword = keyword.strip()

        if not keyword or keyword.isspace():
            return False

        if not KEYWORD_PATTERN.search(keyword):
            raise UnprocessableContent('Invalid keyword')

        return True
