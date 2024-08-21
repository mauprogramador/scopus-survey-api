from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce
from multiprocessing import cpu_count
from os.path import join
from re import sub
from signal import SIGINT, signal
from threading import Event

from bs4 import BeautifulSoup, PageElement, Tag
from fastapi.responses import FileResponse
from fuzzywuzzy.fuzz import WRatio
from pandas import DataFrame

from app.adapters.gateway.api_config import ApiConfig
from app.core.config.config import DIRECTORY, LOG
from app.core.common.patterns import SPACES_PATTERN
from app.core.interfaces import Gateway, UseCase


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
    RATIO = 80

    def __init__(self, scopus_api: Gateway) -> None:
        self.__scopus_api = scopus_api
        self.__file_path = join(DIRECTORY, self.FILENAME)
        self.__dataframe = DataFrame()
        self.__cpu_count = cpu_count()
        self.__shutdown_event = Event()
        signal(SIGINT, self.__handle_interruption)

    def __handle_interruption(self, *_):
        self.__shutdown_event.set()

    def __total_rows(self) -> int:
        return self.__dataframe.shape[0]

    def search_articles(self, data: UseCase.ParamsType) -> FileResponse:
        articles = self.__scopus_api.search_articles(data)
        self.__dataframe = DataFrame(articles)
        del self.__dataframe[self.LINK_COLUMN]

        self.__dataframe = self.__dataframe.drop_duplicates()
        self.__dataframe = self.__dataframe.reset_index(drop=True)
        self.__dataframe.insert(2, self.AUTHORS_COLUMN, '')
        self.__dataframe.insert(5, self.ABSTRACT_COLUMN, '')

        with ThreadPoolExecutor(max_workers=self.__cpu_count) as executor:
            futures = [
                executor.submit(self.__get_scraping_data, index)
                for index in range(self.__total_rows())
            ]
            for index, _ in enumerate(as_completed(futures)):
                LOG.progress(index + 1, self.__total_rows())

            executor.shutdown(wait=True)

        self.__dataframe = self.__dataframe.rename(columns=ApiConfig.MAPPINGS)
        subset = [self.TITLE_COLUMN, self.AUTHORS_COLUMN]
        self.__dataframe = self.__dataframe.drop_duplicates(subset)
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        self.__filter_dataframe_data_by_similarity()
        self.__dataframe.to_csv(self.__file_path, sep=';', index=False)

        return FileResponse(
            self.__file_path,
            status_code=200,
            media_type='text/csv',
            filename=self.FILENAME,
        )

    def __format_names(self, data: Tag) -> str:
        return data.text.strip().replace(',', '')

    def __format_abstract(self, result: str, data: PageElement):
        content = data.text.strip().replace('\n', '')
        content = sub(SPACES_PATTERN, '', content)

        if not content or content.isspace():
            return result

        result += content

        return result

    def __get_scraping_data(self, index: int) -> None:
        if self.__shutdown_event.is_set():
            return None

        scopus_id = self.__dataframe.loc[index, self.SCOPUS_ID_KEY]
        url, template = self.__scopus_api.scraping_article(scopus_id)
        page = BeautifulSoup(template, features=self.PARSER)

        authors_names = page.select(self.AUTHORS_SELECTOR)
        authors_names = ', '.join(map(self.__format_names, authors_names))

        abstract = page.select_one(self.ABSTRACT_SELECTOR)
        if abstract:
            abstract = reduce(self.__format_abstract, abstract, '')

        self.__dataframe.loc[index, self.URL_COLUMN] = url
        self.__dataframe.loc[index, self.AUTHORS_COLUMN] = authors_names
        self.__dataframe.loc[index, self.ABSTRACT_COLUMN] = abstract

        LOG.debug({'authors_names': authors_names, 'abstract': abstract})

        return None

    def __get_row_index(self, title: str) -> int:
        return self.__dataframe.loc[
            self.__dataframe[self.TITLE_COLUMN] == title
        ].index[0]

    def __filter_dataframe_data_by_similarity(self) -> None:
        grouped_dataframe = self.__dataframe.groupby(self.AUTHORS_COLUMN)

        if grouped_dataframe.ngroups == self.__total_rows():
            return None

        similar_titles = []
        LOG.debug(
            {'groups': grouped_dataframe.ngroups, 'rows': self.__total_rows()}
        )

        for _, group in grouped_dataframe:

            if group.shape[0] < 2:
                continue

            titles = group[self.TITLE_COLUMN].tolist()
            LOG.debug({'titles_group': titles})

            if len(titles) == 2:
                if WRatio(titles[0], titles[1]) > self.RATIO:
                    similar_titles.append(self.__get_row_index(titles[0]))
            else:
                for index, title in enumerate(titles[:-1]):
                    similar_titles.extend(
                        self.__get_row_index(title)
                        for comparative_title in titles[index + 1 :]
                        if WRatio(title, comparative_title) > self.RATIO
                    )

        similar_titles = list(set(similar_titles))
        quantity_before = self.__dataframe.shape[0]

        LOG.debug({'similar_titles': similar_titles})

        self.__dataframe = self.__dataframe.drop(similar_titles)
        quantity_result = quantity_before - self.__total_rows()
        total_loss = (quantity_result / quantity_before) * 100

        LOG.info(f'Total Articles Loss: {total_loss:.2f}%')

        return None
