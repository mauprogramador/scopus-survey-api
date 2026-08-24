import itertools

import pandas as pd
from pandas import DataFrame
from thefuzz.fuzz import token_sort_ratio

from src.infra.utils import logger


class SimilarityFilter:
    """Filter articles from identical authors with similar titles"""

    _COLUMNS = ["authors", "title", "date"]
    _SINGLE_ROW = 1
    _PAIR_SIZE = 2  # Two titles

    def __init__(self) -> None:
        """Filter articles from identical authors with similar titles"""
        self._filtered_ds: DataFrame = None
        self._similar_titles: set[int] = set()

    def _drop_single_groups(self, group: DataFrame) -> bool:
        return group.shape[0] > self._SINGLE_ROW

    def _get_group_similar_title_indices(
        self, group: DataFrame, sm_ratio: int
    ) -> None:
        gp_indices = group.index.to_numpy()
        gp_rows_count = len(gp_indices)

        titles = group["title"].to_numpy()
        dates = group["date"].to_numpy()

        if gp_rows_count == 2:  # Two titles

            if token_sort_ratio(titles[0], titles[1]) > sm_ratio:
                # Get oldest publication to remove it
                oldest_date_idx = 0 if dates[0] <= dates[1] else 1
                self._similar_titles.add(int(gp_indices[oldest_date_idx]))

            return None

        gp_row_indices: set[int] = set()
        index_pairs = itertools.combinations(
            range(gp_rows_count), self._PAIR_SIZE
        )

        for idx1, idx2 in index_pairs:
            if token_sort_ratio(titles[idx1], titles[idx2]) > sm_ratio:
                # Add both similar titles
                gp_row_indices.add(int(gp_indices[idx1]))
                gp_row_indices.add(int(gp_indices[idx2]))

        if not gp_row_indices:
            return None

        # Get latest publication to keep it
        similar_titles_subset = self._filtered_ds.loc[list(gp_row_indices)]
        latest_date_idx = similar_titles_subset["date"].idxmax()

        gp_row_indices.discard(latest_date_idx)
        self._similar_titles.update(gp_row_indices)

        return None

    def filter(self, dataset: DataFrame, similarity_ratio: int) -> DataFrame:
        ds_subset = dataset.loc[:, self._COLUMNS].copy()

        ds_subset["date"] = pd.to_datetime(
            ds_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

        self._filtered_ds = ds_subset.dropna(subset=["date"])
        logger.debug(invalid_datetimes=self._filtered_ds.shape[0])

        if self._filtered_ds.shape[0] <= self._SINGLE_ROW:
            return dataset

        grouped_ds = self._filtered_ds.groupby("authors")

        logger.debug(same_authors_count=grouped_ds.ngroups)
        if grouped_ds.ngroups == dataset.shape[0]:
            return dataset

        self._filtered_ds = grouped_ds.filter(self._drop_single_groups)
        grouped_ds = self._filtered_ds.groupby("authors")

        for _, group in grouped_ds:
            self._get_group_similar_title_indices(group, similarity_ratio)

        if not self._similar_titles:
            return dataset

        logger.debug(similar_titles=self._similar_titles)
        similar_titles = list(self._similar_titles)

        dropped_df = dataset.loc[similar_titles]
        logger.debug(dropped_similar=dropped_df)

        dataset = dataset.drop(index=similar_titles)
        dataset = dataset.reset_index(drop=True)

        return dataset
