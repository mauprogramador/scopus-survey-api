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
from src.core.domain.http_exceptions import ServiceUnavailable


class ArticlesSimilarityFilter:
    """Filter articles from identical authors with similar titles"""

    _DATEFMT = "%Y-%m-%d"
    _SINGLE_ROW = 1
    _SIZE = 2

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""
        self._filtered_df: DataFrame = None
        self._ratio: int = None
        try:
            self._workers = min(len(sched_getaffinity(0)) - 1, 4)
        except AttributeError:
            cpu_cores = cpu_count()
            self._workers = cpu_cores - 1 if cpu_cores else 4

    def _drop_singles(self, group: DataFrame) -> bool:
        return group.shape[0] > 1

    @staticmethod
    def _get_similar_title_indexes(
        group: DataFrame, similarity_ratio: int, size: int
    ) -> int | set[int] | None:
        title = group[Column.TITLE]

        if title.shape[0] == 2:
            if ratio(title.iloc[0], title.iloc[1]) > similarity_ratio:
                return int(group[Column.DATE].idxmin())

            return None

        rows_indexes: set[int] = set()

        for indexes in combinations(range(group.shape[0]), size):
            titles = title.iloc[indexes[0]], title.iloc[indexes[1]]

            if ratio(titles[0], titles[1]) > similarity_ratio:
                rows_indexes.add(group.index[indexes[0]])
                rows_indexes.add(group.index[indexes[1]])

        return rows_indexes

    def _get_single_group_index(self, grouped_df: DataFrame) -> set[int]:
        rows_indexes = self._get_similar_title_indexes(
            grouped_df, self._ratio, self._SIZE
        )

        if rows_indexes is None:
            return set()

        if isinstance(rows_indexes, int):
            return {rows_indexes}

        similar_titles_subset = self._filtered_df.iloc[list(rows_indexes)]
        latest_index = similar_titles_subset[Column.DATE].idxmax()
        rows_indexes.discard(latest_index)

        return rows_indexes

    def _handle_groups_similarity(self) -> set[int]:
        grouped_df = self._filtered_df.groupby(Column.AUTHORS)
        similar_titles: set[int] = set()

        if grouped_df.ngroups == 1:
            single_group = next(iter(grouped_df))[1]
            return self._get_single_group_index(single_group)

        max_workers = min(self._filtered_df.shape[0], self._workers)
        LOG.debug({"max_workers": max_workers})

        with ProcessPoolExecutor(max_workers) as executor:
            all_tasks = {
                executor.submit(
                    ArticlesSimilarityFilter._get_similar_title_indexes,
                    group,
                    self._ratio,
                    self._SIZE,
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

                    similar_titles_subset = self._filtered_df.iloc[
                        list(rows_indexes)
                    ]
                    latest_index = similar_titles_subset[Column.DATE].idxmax()

                    rows_indexes.discard(latest_index)
                    similar_titles.update(rows_indexes)

                except (CancelledError, Exception) as exc:

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        return similar_titles

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        df_subset = dataframe.loc[:, Column.FILTER].copy()
        self._ratio = similarity_ratio

        df_subset[Column.DATE] = to_datetime(
            df_subset[Column.DATE],
            yearfirst=True,
            format=self._DATEFMT,
            errors="coerce",
        )

        self._filtered_df = df_subset.dropna(subset=[Column.DATE])
        LOG.debug({"invalids_datetime": self._filtered_df.shape[0]})

        if self._filtered_df.shape[0] <= self._SINGLE_ROW:
            return dataframe

        grouped_df = self._filtered_df.groupby(Column.AUTHORS)

        LOG.debug({"same_authors_count": grouped_df.ngroups})
        if grouped_df.ngroups == dataframe.shape[0]:
            return dataframe

        self._filtered_df = grouped_df.filter(self._drop_singles)
        similar_titles = self._handle_groups_similarity()

        if not similar_titles:
            return dataframe

        LOG.debug({"similar_titles": similar_titles})

        dataframe = dataframe.drop(list(similar_titles))
        dataframe = dataframe.reset_index(drop=True)

        return dataframe
