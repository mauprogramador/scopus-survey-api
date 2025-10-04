from src.core.common.types import ResponseBundle
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.data.serializers import ScopusHeaders, ScopusSearch


class SurveyDetails:
    """Gather Scopus API search and quota details"""

    def __init__(self) -> None:
        """Gather Scopus API search and quota details"""
        self._headers: dict[str, str] = {}
        self._log_data: tuple[ScopusHeaders, int] = None

    def set_search_data(self, scopus_search: ScopusSearch) -> None:
        if scopus_search.total_results > MAX_ITEMS_PER_PAGE:
            scopus_search.items_per_page = MAX_ITEMS_PER_PAGE

        self._headers.update(
            {
                "X-Total": str(scopus_search.total_results),
                "X-Items-Per-Page": str(scopus_search.items_per_page),
                "X-Pages-Count": str(scopus_search.pages_count),
            }
        )

    def set_search_quota(self, response: ResponseBundle) -> None:
        quota = ScopusHeaders.model_validate(response.headers)
        self._log_data = (quota, response.code)
        self._headers.update(
            {
                "X-Search-Limit": str(quota.limit),
                "X-Search-Remaining": str(quota.remaining),
                "X-Search-Reset": str(quota.reset_datetime),
                "X-Search-ELS-Status": quota.status,
            }
        )

    def set_abstract_quota(self, response: ResponseBundle) -> None:
        quota = ScopusHeaders.model_validate(response.headers)
        self._log_data = (quota, response.code)
        self._headers.update(
            {
                "X-Abstract-Limit": str(quota.limit),
                "X-Abstract-Remaining": str(quota.remaining),
                "X-Abstract-Reset": str(quota.reset_datetime),
                "X-Abstract-ELS-Status": quota.status,
            }
        )

    def set_loss(self, loss_amount: int, loss_percent: float) -> None:
        loss = f"{loss_amount}doc / {loss_percent:.2f}%"
        self._headers.update({"X-Loss": loss})

    def set_average_found(self, average: int) -> None:
        self._headers.update({"X-Average-Found": f"~{average:,}"})

    @property
    def log_data(self) -> tuple[ScopusHeaders, int]:
        return self._log_data

    @property
    def headers(self) -> dict[str, str]:
        return self._headers
