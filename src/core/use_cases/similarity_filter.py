import itertools
import os

import pandas as pd
from pandas import DataFrame
from thefuzz.fuzz import ratio as fuzz_ratio

from src.infra.utils import logger


class SimilarityFilter:
    """Filter articles from identical authors with similar titles"""

    _COLUMNS = ["authors", "title", "date"]
    _SINGLE_ROW = 1
    _SIZE = 2  # Two titles

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""
        self._filtered_df: DataFrame = None
        self._ratio: int = None
        try:
            self._workers = min(len(os.sched_getaffinity(0)) - 1, 4)
        except AttributeError:
            cpu_cores = os.cpu_count()
            self._workers = cpu_cores - 1 if cpu_cores else 4

    def _drop_singles(self, group: DataFrame) -> bool:
        return group.shape[0] > self._SINGLE_ROW

    def _get_similar_title_indexes(
        self, group: DataFrame
    ) -> int | set[int] | None:
        indexes = group.index.to_numpy()
        num_rows = len(indexes)

        titles = group["title"].to_numpy()
        dates = group["date"].to_numpy()

        if num_rows == self._SIZE:
            if fuzz_ratio(titles[0], titles[1]) > self._ratio:
                min_date_idx = 0 if dates[0] <= dates[1] else 1
                return int(indexes[min_date_idx])
            return None

        rows_indexes: set[int] = set()
        arrangements = itertools.combinations(range(num_rows), self._SIZE)

        for idx1, idx2 in arrangements:
            if fuzz_ratio(titles[idx1], titles[idx2]) > self._ratio:
                rows_indexes.add(int(indexes[idx1]))
                rows_indexes.add(int(indexes[idx2]))

        if not rows_indexes:
            return None

        return rows_indexes

    def _get_single_group_index(self, grouped_df: DataFrame) -> set[int]:
        rows_indexes = self._get_similar_title_indexes(grouped_df)

        if rows_indexes is None:
            return set()

        if isinstance(rows_indexes, int):
            return {rows_indexes}

        similar_titles_subset = self._filtered_df.loc[list(rows_indexes)]
        latest_index = similar_titles_subset["date"].idxmax()
        rows_indexes.discard(latest_index)

        return rows_indexes

    def _handle_groups_similarity(self) -> set[int]:
        grouped_df = self._filtered_df.groupby("authors")
        similar_titles: set[int] = set()

        if grouped_df.ngroups == 1:
            single_group = next(iter(grouped_df))[1]
            return self._get_single_group_index(single_group)

        max_workers = min(self._filtered_df.shape[0], self._workers)
        logger.debug({"max_workers": max_workers})

        for _, group in grouped_df:

            rows_indexes = self._get_similar_title_indexes(group)

            if rows_indexes is None:
                continue

            if isinstance(rows_indexes, int):
                similar_titles.add(rows_indexes)
                continue

            similar_titles_subset = self._filtered_df.loc[list(rows_indexes)]
            latest_index = similar_titles_subset["date"].idxmax()

            rows_indexes.discard(latest_index)
            similar_titles.update(rows_indexes)

        return similar_titles

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        df_subset = dataframe.loc[:, self._COLUMNS].copy()
        self._ratio = similarity_ratio

        df_subset["date"] = pd.to_datetime(
            df_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

        self._filtered_df = df_subset.dropna(subset=["date"])
        logger.debug({"invalids_datetime": self._filtered_df.shape[0]})

        if self._filtered_df.shape[0] <= self._SINGLE_ROW:
            return dataframe

        grouped_df = self._filtered_df.groupby("authors")

        logger.debug({"same_authors_count": grouped_df.ngroups})
        if grouped_df.ngroups == dataframe.shape[0]:
            return dataframe

        self._filtered_df = grouped_df.filter(self._drop_singles)
        similar_titles = self._handle_groups_similarity()

        if not similar_titles:
            return dataframe

        logger.debug({"similar_titles": similar_titles})

        dataframe = dataframe.drop(list(similar_titles))
        dataframe = dataframe.reset_index(drop=True)

        return dataframe
