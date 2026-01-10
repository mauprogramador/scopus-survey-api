from math import ceil

from src.core.common.error_messages import QUOTA_EXCEEDED
from src.core.common.types import Json, Quota
from src.core.data.serializers import ScopusSearch
from src.core.domain.http_exceptions import TooManyRequests


class QuotaResultsHandler:
    """Gathers the Scopus data while managing the quotas"""

    _FIRST_ABSTRACT = 1

    def __init__(self, first_search: ScopusSearch) -> None:
        """Gathers the Scopus data while managing the quotas"""
        self.total_results = first_search.total_results
        self.items_per_page = first_search.items_per_page
        self.entry = [*first_search.entry]
        self.abstracts: list[Json] = []
        self.total_abstracts = first_search.total_results

        if self.total_results == 0:
            self.pages_count = 0
        else:
            self.pages_count = ceil(self.total_results / self.items_per_page)

    def _check_quota(self, quota: tuple[Quota, int]) -> int:
        remaining_quota = quota[0].remaining

        if remaining_quota == 0:
            raise TooManyRequests(QUOTA_EXCEEDED)

        return remaining_quota

    def handle_search_quota(self, quota: tuple[Quota, int]) -> None:
        remaining_quota = self._check_quota(quota)
        possible_searches = remaining_quota * self.items_per_page

        if self.total_results > possible_searches:
            self.total_results = possible_searches + len(self.entry)
            self.total_abstracts = self.total_results
            self.pages_count = ceil(self.total_results / self.items_per_page)

    def handle_abstract_quota(self, quota: tuple[Quota, int]) -> None:
        remaining_quota = self._check_quota(quota)

        if self.total_abstracts > remaining_quota:
            self.total_abstracts = remaining_quota + self._FIRST_ABSTRACT

        if self.total_abstracts > 2:
            self.entry = self.entry[1 : self.total_abstracts + 1]
