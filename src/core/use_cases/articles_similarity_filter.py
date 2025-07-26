from concurrent.futures import (
    CancelledError,
    ProcessPoolExecutor,
    as_completed,
)
from itertools import combinations
from os import cpu_count, sched_getaffinity

from pandas import DataFrame, to_datetime
from thefuzz.fuzz import ratio  # type: ignore

from src.core.common.error_messages import CANCELLED_ERROR
from src.core.config.config import LOG
from src.core.data.enums import Column


class ArticlesSimilarityFilter:
    """Filter articles from identical authors with similar titles"""

    __DATEFMT = "%Y-%m-%d"
    __SIZE = 2

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""
        try:
            self.__workers = min(len(sched_getaffinity(0)) - 1, 4)
        except AttributeError:
            cpu_cores = cpu_count()
            self.__workers = cpu_cores - 1 if cpu_cores else 4

    def __drop_singles(self, group: DataFrame) -> bool:
        return group.shape[0] > 1

    @staticmethod
    def _process_group(group: DataFrame, similarity_ratio: int):
        title = group[Column.TITLE]

        if title.shape[0] == 2:
            if ratio(title.iloc[0], title.iloc[1]) > similarity_ratio:
                return int(group[Column.DATE].idxmax())

            return None

        rows_indexes: set[int] = set()
        size = ArticlesSimilarityFilter.__SIZE

        for indexes in combinations(range(group.shape[0]), size):
            titles = title.iloc[indexes[0]], title.iloc[indexes[1]]

            if ratio(titles[0], titles[1]) > similarity_ratio:
                rows_indexes.add(group.index[indexes[0]])
                rows_indexes.add(group.index[indexes[1]])

        return rows_indexes

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

        max_workers = min(dataframe.shape[0], self.__workers)
        LOG.debug({"max_workers": max_workers})

        with ProcessPoolExecutor(max_workers) as executor:
            all_tasks = {
                executor.submit(
                    ArticlesSimilarityFilter._process_group,
                    group,
                    similarity_ratio,
                )
                for _, group in grouped_df
            }
            remaining_tasks = all_tasks.copy()

            for future in as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    rows_indexes = future.result()
                    if rows_indexes is None:
                        continue

                    if isinstance(rows_indexes, int):
                        similar_titles.add(rows_indexes)
                        continue

                    similar_titles_subset = filtered_df.iloc[
                        list(rows_indexes)
                    ]
                    latest_index = similar_titles_subset[Column.DATE].idxmin()

                    rows_indexes.discard(latest_index)
                    similar_titles.update(rows_indexes)

                except (CancelledError, Exception) as exc:
                    LOG.error(CANCELLED_ERROR)

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    raise exc

        if not similar_titles:
            return dataframe

        LOG.debug({"similar_titles": similar_titles})

        dataframe = dataframe.drop(list(similar_titles))
        dataframe = dataframe.reset_index(drop=True)

        return dataframe
