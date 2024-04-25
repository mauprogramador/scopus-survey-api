from functools import reduce
from os.path import join
from re import sub

from bs4 import BeautifulSoup, PageElement, Tag
from fastapi.responses import FileResponse
from fuzzywuzzy.fuzz import WRatio
from pandas import DataFrame, Series

from app.adapters.gateway.api_config import ApiConfig
from app.adapters.gateway.scopus_api import ScopusApi
from app.core.config import DIRECTORY, LOG, SPACES_PATTERN
from app.core.interfaces import UseCase


class Scopus(UseCase):
    AUTHORS_SELECTOR = '#authorlist .list-inline li .previewTxt'
    ABSTRACT_SELECTOR = '#abstractSection p'
    SCOPUS_ID_KEY = 'dc:identifier'
    PARSER = 'html.parser'
    AUTHORS_COLUMN = 'Authors'
    ABSTRACT_COLUMN = 'Abstract'
    URL_COLUMN = 'prism:url'
    TITLE_COLUMN = 'Title'
    LINK_COLUMN = '@_fa'
    FILENAME = 'articles.csv'

    def __init__(self) -> None:
        self.__file_path = join(DIRECTORY, self.FILENAME)
        self.__dataframe = DataFrame()

    def search_articles(self, data: UseCase.ParamsType) -> FileResponse:
        articles = ScopusApi.search_articles(data)
        dataframe = DataFrame(articles)
        del dataframe[self.LINK_COLUMN]

        dataframe = dataframe.drop_duplicates()
        dataframe.insert(2, self.AUTHORS_COLUMN, '')
        dataframe.insert(5, self.ABSTRACT_COLUMN, '')

        dataframe: DataFrame = dataframe.apply(
            self.__get_scraping_data, axis=1, raw=False, result_type='reduce'
        )

        dataframe = dataframe.rename(columns=ApiConfig.MAPPINGS)
        subset = [self.TITLE_COLUMN, self.AUTHORS_COLUMN]
        dataframe = dataframe.drop_duplicates(subset)

        dataframe = self.__filter_dataframe(dataframe)
        dataframe.to_csv(self.__file_path, sep=';', index=False)

        return FileResponse(
            self.__file_path,
            status_code=200,
            media_type='text/csv',
            filename=self.FILENAME,
        )

    def __format_abstract(self, result: str, data: PageElement):
        content = data.text.strip().replace('\n', '')
        content = sub(SPACES_PATTERN, '', content)

        if not content or content.isspace():
            return result

        result += content

        return result

    def __format_names(self, data: Tag) -> str:
        return data.text.strip().replace(',', '')

    def __get_scraping_data(self, row: Series) -> Series:
        url, template = ScopusApi.scraping_article(row[self.SCOPUS_ID_KEY])
        page = BeautifulSoup(template, features=self.PARSER)

        authors_names = page.select(self.AUTHORS_SELECTOR)
        authors_names = ', '.join(map(self.__format_names, authors_names))

        abstract = page.select_one(self.ABSTRACT_SELECTOR)
        if abstract:
            abstract = reduce(self.__format_abstract, abstract, '')

        row[self.URL_COLUMN] = url
        row[self.AUTHORS_COLUMN] = authors_names
        row[self.ABSTRACT_COLUMN] = abstract

        LOG.debug({'authors_names': authors_names, 'abstract': abstract})

        return row

    def __get_row_index(self, title: str) -> int:
        return self.__dataframe.loc[
            self.__dataframe[self.TITLE_COLUMN] == title
        ].index[0]

    def __filter_dataframe(self, dataframe: DataFrame) -> DataFrame:
        grouped_dataframe = dataframe.groupby(self.AUTHORS_COLUMN)

        if grouped_dataframe.ngroups == dataframe.shape[0]:
            return dataframe

        similar_titles = []
        self.__dataframe = dataframe
        LOG.debug(
            {'groups': grouped_dataframe.ngroups, 'rows': dataframe.shape[0]}
        )

        for _, group in grouped_dataframe:

            if group.shape[0] < 2:
                continue

            titles = group[self.TITLE_COLUMN].tolist()
            LOG.debug({'titles_group': titles})

            if len(titles) == 2:
                if WRatio(titles[0], titles[1]) > 80:
                    similar_titles.append(self.__get_row_index(titles[0]))
            else:
                for index, title in enumerate(titles[:-1]):
                    similar_titles.extend(
                        self.__get_row_index(title)
                        for comparative_title in titles[index + 1 :]
                        if WRatio(title, comparative_title) > 80
                    )

        similar_titles = list(set(similar_titles))
        rows_before = dataframe.shape[0]

        LOG.debug({'similar_titles': similar_titles})

        dataframe = dataframe.drop(similar_titles)
        total_loss = ((rows_before - dataframe.shape[0]) / rows_before) * 100

        LOG.info(f'Total Articles Loss: {total_loss:.2f}%')

        return dataframe
