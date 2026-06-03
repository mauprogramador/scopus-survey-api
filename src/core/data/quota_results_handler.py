from math import ceil

from src.core.common.types import Json, Quota
from src.core.data.enums import ExcMsg
from src.core.data.serializers import ScopusEntry, ScopusSearch
from src.core.domain.http_exceptions import BadGateway, NotFound


class QuotaResultsHandler:
    """Gathers the Scopus data while managing the quotas"""

    _FIRST_RESULT = 1
    _RANGE_OFFSET = 1

    def __init__(self) -> None:
        """Gathers the Scopus data while managing the quotas"""
        self.total_results: int = None
        self.items_per_page: int = None
        self.entry: list[ScopusEntry] = None
        self.pages_count: int = None
        self.total_abstracts: int = None
        self.abstracts: list[Json] = None

    @property
    def pages_to_fetch(self) -> int:
        return self.pages_count - self._FIRST_RESULT

    @property
    def pages_to_fetch_range(self) -> range:
        return range(self._FIRST_RESULT, self.pages_count)

    @property
    def pages_to_fetch_progress(self) -> tuple[int, int, int]:
        return self.total_results, self.items_per_page, self._FIRST_RESULT

    @property
    def abstracts_to_fetch(self) -> int:
        return self.total_abstracts - self._FIRST_RESULT

    @property
    def abstracts_to_fetch_range(self) -> range:
        return range(self._FIRST_RESULT, self.total_abstracts)

    def set_first_search(self, first_search: ScopusSearch) -> None:
        self.total_results = first_search.total_results
        self.items_per_page = first_search.items_per_page
        self.entry = [*first_search.entry]

        if self.total_results == 0:
            raise NotFound(ExcMsg.ARTICLES_NOT_FOUND)

        self.pages_count = ceil(self.total_results / self.items_per_page)

    def validate_integrity(self) -> None:
        if self.total_results != len(self.entry):
            raise BadGateway(ExcMsg.DATA_MISMATCH_ERROR)

    def fix_total(self) -> None:
        self.total_abstracts = len(self.entry)
        self.abstracts = []

    def handle_search_quota(self, quota: tuple[Quota, int]) -> None:
        possible_searches = quota[0].remaining * self.items_per_page

        if self.total_results > possible_searches:
            self.total_results = possible_searches + len(self.entry)
            self.pages_count = ceil(self.total_results / self.items_per_page)

    def handle_abstract_quota(self, quota: tuple[Quota, int]) -> None:
        if self.total_abstracts > quota[0].remaining:
            self.total_abstracts = quota[0].remaining + self._FIRST_RESULT
