from requests import Response

from src.core.data.serializers import ScopusQuotaRateLimit, ScopusSearch


class SurveyDetail:

    def __init__(self) -> None:
        self.__scopus_search: ScopusSearch = None
        self.quota: ScopusQuotaRateLimit = None
        self.code: int = None
        self.max_count: int = None

    def set_scopus_search(self, scopus_search: ScopusSearch) -> None:
        self.__scopus_search = scopus_search

    def set_response(self, response: Response) -> None:
        self.quota = ScopusQuotaRateLimit.model_validate(response.headers)
        self.code = response.status_code

    @property
    def log_data(self) -> tuple[ScopusQuotaRateLimit, int]:
        return self.quota, self.code

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-Limit": str(self.quota.limit),
            "X-Remaining": str(self.quota.remaining),
            "X-Reset": str(self.quota.reset),
            "X-ELS-Status": str(self.quota.status),
            "X-Total": str(self.__scopus_search.total_results),
            "X-Items-Per-Page": str(self.__scopus_search.items_per_page),
            "X-Pages-Count": str(self.__scopus_search.pages_count),
            "X-Max-Count": str(self.max_count),
        }
