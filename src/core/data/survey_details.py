from src.core.common.types import ResponseBundle
from src.core.config.scopus import BOOLEAN_OPERATOR, MAX_ITEMS_PER_PAGE
from src.core.data.serializers import ScopusHeaders, ScopusPage


class SurveyDetails:
    """Gather Scopus API search and quota details"""

    def __init__(self) -> None:
        """Gather Scopus API search and quota details"""
        self.headers: dict[str, str] = {}
        self.metadata: list[str] = []
        self.search_quota: tuple[ScopusHeaders, int] = None
        self.abstract_quota: tuple[ScopusHeaders, int] = None

    def set_keywords(self, keywords: list[str]) -> None:
        self.headers.update({"X-Keywords": BOOLEAN_OPERATOR.join(keywords)})

    def set_combination(self, combination: str) -> None:
        self.headers.update({"X-Combination": combination})

    def set_search_data(self, scopus_search: ScopusPage) -> None:
        if scopus_search.total_results > MAX_ITEMS_PER_PAGE:
            scopus_search.items_per_page = MAX_ITEMS_PER_PAGE

        self.headers.update(
            {
                "X-Total": str(scopus_search.total_results),
                "X-Items-Per-Page": str(scopus_search.items_per_page),
                "X-Pages-Count": str(scopus_search.pages_count),
            }
        )

        self.metadata.extend(
            [
                f"total={scopus_search.total_results}",
                f"items_per_page={scopus_search.items_per_page}",
                f"pages_count={scopus_search.pages_count}",
            ]
        )

    def set_search_quota(self, res: ResponseBundle) -> None:
        quota = ScopusHeaders.model_validate(res.headers)
        self.search_quota = (quota, res.code)
        self.headers.update(
            {
                "X-Search-Limit": str(quota.limit),
                "X-Search-Remaining": str(quota.remaining),
                "X-Search-Reset": str(quota.reset_datetime),
            }
        )

    def set_abstract_quota(self, res: ResponseBundle) -> None:
        quota = ScopusHeaders.model_validate(res.headers)
        self.abstract_quota = (quota, res.code)
        self.headers.update(
            {
                "X-Abstract-Limit": str(quota.limit),
                "X-Abstract-Remaining": str(quota.remaining),
                "X-Abstract-Reset": str(quota.reset_datetime),
            }
        )

    def set_results(self, retrieved: int) -> None:
        total = int(self.headers["X-Total"])
        results = f"{retrieved:,}doc / {total:,}doc"
        self.headers.update({"X-Results": results})
        self.metadata.append(f"results={results}")

    def set_loss(self, loss_amount: int, loss_percent: float) -> None:
        loss = f"{loss_amount}doc / {loss_percent:.2f}%"
        self.headers.update({"X-Loss": loss})
        self.metadata.append(f"loss={loss}")
