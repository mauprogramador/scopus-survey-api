from pandas import DataFrame, to_datetime
from thefuzz.fuzz import ratio  # type: ignore

from src.core.config.config import LOG
from src.core.data.enums import Column
from src.core.domain.interfaces import SimilarityFilterABC


class ArticlesSimilarityFilter(SimilarityFilterABC):
    """Filter articles from identical authors with similar titles"""

    __DATEFMT = "%Y-%m-%d"

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        grouped_df = dataframe[Column.FILTER].groupby(Column.AUTHORS)

        LOG.debug({"same_authors_count": grouped_df.ngroups})
        if grouped_df.ngroups == dataframe.shape[0]:
            return dataframe

        filtered_df = grouped_df.filter(self.__drop_singles)
        filtered_df[Column.DATE] = to_datetime(
            filtered_df[Column.DATE], yearfirst=True, format=self.__DATEFMT
        )

        grouped_df = filtered_df.groupby(Column.AUTHORS)
        similar_titles: set[int] = set()

        for _, group in grouped_df:
            title = group[Column.TITLE]

            if title.shape[0] == 2:
                if ratio(title.iloc[0], title.iloc[1]) > similarity_ratio:
                    oldest_index = group[Column.DATE].idxmax()
                    similar_titles.add(oldest_index)
                continue

            rows_indexes: set[int] = set()

            for outer_index in range(group.shape[0]):
                for inner_index in range(outer_index + 1, group.shape[0]):
                    titles = title.iloc[outer_index], title.iloc[inner_index]

                    if ratio(titles[0], titles[1]) > similarity_ratio:
                        rows_indexes.add(group.index[outer_index])
                        rows_indexes.add(group.index[inner_index])

            similar_titles_subset = filtered_df.iloc[list(rows_indexes)]
            latest_index = similar_titles_subset[Column.DATE].idxmin()

            rows_indexes.discard(latest_index)
            similar_titles.update(rows_indexes)

        if not similar_titles:
            return dataframe

        LOG.debug({"similar_titles": similar_titles})

        dataframe = dataframe.drop(list(similar_titles))
        dataframe = dataframe.reset_index(drop=True)

        return dataframe

    def __drop_singles(self, group: DataFrame) -> bool:
        return group.shape[0] > 1
