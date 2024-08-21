from re import sub

from bs4 import BeautifulSoup, Tag
from pandas import DataFrame

from app.core.common.patterns import SPACES_PATTERN
from app.core.config.config import HANDLER
from app.core.config.scopus import (
    ABSTRACT_SELECTOR,
    AUTHORS_SELECTOR,
    NULL,
    TEMPLATE_COLUMN,
    URL_COLUMN,
)
from app.core.data.dtos import ScrapeData
from app.core.domain.exceptions import InterruptError
from app.core.domain.metaclasses import ArticlesPage, ArticlesScraper


class ArticlesPageScraper(ArticlesScraper):
    """Download article pages, parse the HTML, and scrape their data"""

    __PARSER = "html.parser"

    def __init__(
        self,
        articles_page: ArticlesPage,
    ) -> None:
        """Download article pages, parse the HTML, and scrape their data"""
        self.__articles_page = articles_page
        self.__subset: DataFrame = None

    def set_subset(self, subset: DataFrame) -> None:
        self.__subset = self.__articles_page.get_articles_page(subset)

    def scrape(self, index: int) -> ScrapeData:
        if HANDLER.event.is_set():
            raise InterruptError()

        url = self.__subset.loc[index, URL_COLUMN]
        template = self.__subset.loc[index, TEMPLATE_COLUMN]

        if template == NULL:
            return ScrapeData(index, str(url), NULL, NULL)

        page = BeautifulSoup(template, features=self.__PARSER)
        author_name_tags = page.select(AUTHORS_SELECTOR)
        authors_names = ", ".join(map(self.__format_names, author_name_tags))

        abstract_tag = page.select_one(ABSTRACT_SELECTOR)
        abstract = self.__format_abstract(abstract_tag)

        return ScrapeData(index, str(url), authors_names, abstract)

    def __format_names(self, data: Tag) -> str:
        content = data.text.strip().replace(",", "")
        return content if content and not content.isspace() else NULL

    def __format_abstract(self, data: Tag | None) -> str:
        if data is None:
            return NULL

        content = data.text.strip().replace("\n", "")
        content = sub(SPACES_PATTERN, " ", content)

        return content if content and not content.isspace() else NULL
