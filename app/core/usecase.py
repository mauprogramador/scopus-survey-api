from functools import reduce
from os.path import join
from re import sub

from bs4 import BeautifulSoup, PageElement, Tag
from fastapi.responses import FileResponse
from pandas import DataFrame, Series

from app.core.config import DIRECTORY, SPACES_PATTERN
from app.core.interfaces import UseCase
from app.gateway.api_config import ApiConfig
from app.gateway.scopus_api import ScopusApi


class Scopus(UseCase):
    AUTHORS_SELECTOR = '#authorlist .list-inline li .previewTxt'
    ABSTRACT_SELECTOR = '#abstractSection p'
    SCOPUS_ID_KEY = 'dc:identifier'
    PARSER = 'html.parser'
    AUTHORS_COLUMN = 'Authors'
    ABSTRACT_COLUMN = 'Abstract'
    URL_COLUMN = 'prism:url'
    TITLE_COLUMN = 'Title'
    FILENAME = 'articles.csv'

    @classmethod
    def __format_abstract(cls, result: str, data: PageElement):
        content = data.text.strip().replace('\n', '')
        content = sub(SPACES_PATTERN, '', content)

        if not content or content.isspace():
            return result

        result = result + content

        return result

    @classmethod
    def __format_names(cls, data: Tag) -> str:
        return data.text.strip().replace(',', '')

    @classmethod
    def __get_scraping_data(cls, row: Series):
        url, template = ScopusApi.scraping_article(row[cls.SCOPUS_ID_KEY])
        page = BeautifulSoup(template, features=cls.PARSER)

        authors_names = page.select(cls.AUTHORS_SELECTOR)
        authors_names = ', '.join(map(cls.__format_names, authors_names))

        abstract = page.select_one(cls.ABSTRACT_SELECTOR)
        if abstract:
            abstract = reduce(cls.__format_abstract, abstract, '')

        row[cls.URL_COLUMN] = url
        row[cls.AUTHORS_COLUMN] = authors_names
        row[cls.ABSTRACT_COLUMN] = abstract

        return row

    @classmethod
    def search_articles(cls, data: UseCase.ParamsType) -> FileResponse:
        articles = ScopusApi.search_articles(data)
        dataframe = DataFrame(articles)
        del dataframe['@_fa']

        dataframe = dataframe.drop_duplicates()
        dataframe.insert(2, cls.AUTHORS_COLUMN, '')
        dataframe.insert(5, cls.ABSTRACT_COLUMN, '')

        dataframe: DataFrame = dataframe.apply(
            cls.__get_scraping_data, axis=1, raw=False, result_type='reduce'
        )

        dataframe = dataframe.rename(columns=ApiConfig.MAPPINGS)
        subset = [cls.TITLE_COLUMN, cls.AUTHORS_COLUMN]
        dataframe = dataframe.drop_duplicates(subset, keep=False)

        file_path = join(DIRECTORY, cls.FILENAME)
        dataframe.to_csv(file_path, sep=';', index=False)

        return FileResponse(
            file_path,
            status_code=200,
            media_type='text/csv',
            filename=cls.FILENAME,
        )
