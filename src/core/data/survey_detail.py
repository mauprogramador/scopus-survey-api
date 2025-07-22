from src.core.common.types import ResponseBundle
from src.core.data.serializers import ScopusQuotaRateLimit, ScopusSearch


class SurveyDetail:
    """Gather Scopus API search and quota details"""

    def __init__(self) -> None:
        """Gather Scopus API search and quota details"""
        self.__headers: dict[str, str] = {}
        self.__log_data: tuple[ScopusQuotaRateLimit, int] = None

    def set_max_count(self, max_count: int) -> None:
        self.__headers.update({"X-Max-Count": str(max_count)})

    def set_search_data(self, scopus_search: ScopusSearch) -> None:
        self.__headers.update(
            {
                "X-Total": str(scopus_search.total_results),
                "X-Items-Per-Page": str(scopus_search.items_per_page),
                "X-Pages-Count": str(scopus_search.pages_count),
            }
        )

    def set_quota_data(self, response: ResponseBundle) -> None:
        quota = ScopusQuotaRateLimit.model_validate(response.headers)
        self.__log_data = (quota, response.code)
        self.__headers.update(
            {
                "X-Limit": str(quota.limit),
                "X-Remaining": str(quota.remaining),
                "X-Reset": str(quota.reset),
                "X-ELS-Status": quota.status,
            }
        )

    def set_loss(self, loss: float) -> None:
        self.__headers.update({"X-Loss": f"{loss:.2f}%"})

    @property
    def log_data(self) -> tuple[ScopusQuotaRateLimit, int]:
        return self.__log_data

    @property
    def headers(self) -> dict[str, str]:
        return self.__headers
