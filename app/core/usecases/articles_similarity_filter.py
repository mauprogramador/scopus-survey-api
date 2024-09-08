from thefuzz.fuzz import ratio
from pandas import DataFrame

from app.core.config.config import LOG
from app.core.config.scopus import AUTHORS_COLUMN, TITLE_COLUMN
from app.core.domain.metaclasses import SimilarityFilter


class ArticlesSimilarityFilter(SimilarityFilter):
    """Filter articles from identical authors with similar titles"""

    __RATIO = 80

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""
        self.__dataframe: DataFrame = None
        self.__subset: DataFrame = None

    def filter(self, dataframe: DataFrame) -> DataFrame:
        self.__dataframe = dataframe
        self.__subset = dataframe[[AUTHORS_COLUMN, TITLE_COLUMN]]

        authors_counts = self.__subset[AUTHORS_COLUMN].value_counts()
        repeated_authors = authors_counts[authors_counts >= 2].index

        LOG.debug({"authors_counts": authors_counts.shape[0]})
        if authors_counts.shape[0] == self.__dataframe.shape[0]:
            return self.__dataframe

        similar_titles = set()

        for authors in repeated_authors:
            titles = self.__get_authors_titles(authors)

            if len(titles) == 2:
                if ratio(titles[0], titles[1]) > self.__RATIO:
                    similar_titles.add(self.__get_row_index(titles[0]))
                continue

            for index, title in enumerate(titles[:-1], start=1):
                for comparative_title in titles[index:]:
                    if ratio(title, comparative_title) > self.__RATIO:
                        similar_titles.add(self.__get_row_index(title))
                        break

        if not similar_titles:
            return self.__dataframe

        LOG.debug({"similar_titles": similar_titles})

        self.__dataframe = self.__dataframe.drop(list(similar_titles))
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        return self.__dataframe

    def __get_authors_titles(self, authors: str) -> list[str]:
        selector = self.__subset[AUTHORS_COLUMN] == authors
        return self.__subset.loc[selector][TITLE_COLUMN].tolist()

    def __get_row_index(self, title: str) -> int:
        selector = self.__dataframe[TITLE_COLUMN] == title
        return self.__dataframe.loc[selector].index[0]
