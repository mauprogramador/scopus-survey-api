from src.core.common.types import ResponseBundle
from src.core.data.serializers import ScopusHeaders, ScopusSearch


class SurveyDetail:
    """Gather Scopus API search and quota details"""

    def __init__(self) -> None:
        """Gather Scopus API search and quota details"""
        self._headers: dict[str, str] = {}
        self._log_data: tuple[ScopusHeaders, int] = None

    def set_max_count(self, max_count: int) -> None:
        self._headers.update({"X-Max-Count": str(max_count)})

    def set_search_data(self, scopus_search: ScopusSearch) -> None:
        self._headers.update(
            {
                "X-Total": str(scopus_search.total_results),
                "X-Items-Per-Page": str(scopus_search.items_per_page),
                "X-Pages-Count": str(scopus_search.pages_count),
            }
        )

    def set_quota_data(self, response: ResponseBundle) -> None:
        quota = ScopusHeaders.model_validate(response.headers)
        self._log_data = (quota, response.code)
        self._headers.update(
            {
                "X-Limit": str(quota.limit),
                "X-Remaining": str(quota.remaining),
                "X-Reset": str(quota.reset_datetime),
                "X-ELS-Status": quota.status,
            }
        )

    def set_loss(self, loss: float) -> None:
        self._headers.update({"X-Loss": f"{loss:.2f}%"})

    @property
    def log_data(self) -> tuple[ScopusHeaders, int]:
        return self._log_data

    @property
    def headers(self) -> dict[str, str]:
        return self._headers
