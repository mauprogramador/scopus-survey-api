import itertools

import pandas as pd
from pandas import DataFrame
from thefuzz.fuzz import token_sort_ratio

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
            if token_sort_ratio(titles[0], titles[1]) > self._ratio:
                min_date_idx = 0 if dates[0] <= dates[1] else 1
                return int(indexes[min_date_idx])
            return None

        rows_indexes: set[int] = set()
        arrangements = itertools.combinations(range(num_rows), self._SIZE)

        for idx1, idx2 in arrangements:
            if token_sort_ratio(titles[idx1], titles[idx2]) > self._ratio:
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

    def filter(self, dataset: DataFrame, similarity_ratio: int) -> DataFrame:
        df_subset = dataset.loc[:, self._COLUMNS].copy()
        self._ratio = similarity_ratio

        df_subset["date"] = pd.to_datetime(
            df_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

        self._filtered_df = df_subset.dropna(subset=["date"])
        logger.debug(invalid_datetimes=self._filtered_df.shape[0])

        if self._filtered_df.shape[0] <= self._SINGLE_ROW:
            return dataset

        grouped_df = self._filtered_df.groupby("authors")

        logger.debug(same_authors_count=grouped_df.ngroups)
        if grouped_df.ngroups == dataset.shape[0]:
            return dataset

        self._filtered_df = grouped_df.filter(self._drop_singles)
        similar_titles = self._handle_groups_similarity()

        if not similar_titles:
            return dataset

        logger.debug(similar_titles=similar_titles)

        dropped_df = dataset.loc[list(similar_titles)]
        logger.debug(dropped_similar=dropped_df)

        dataset = dataset.drop(index=list(similar_titles))
        dataset = dataset.reset_index(drop=True)

        return dataset
