import math
from dataclasses import dataclass, field

from src.core.domain.types import Headers, Json, ScopusEntry, ScopusPage


@dataclass
class ScopusContext:
    search_result: ScopusPage = None
    total_results: int = None
    search_headers: Headers = None
    abstract_headers: Headers = None
    entry: list[ScopusEntry] = field(default_factory=list)
    abstracts: list[Json] = field(default_factory=list)

    @property
    def items_per_page(self) -> int:
        if self.search_result:
            return self.search_result.items_per_page
        return 0

    @property
    def pages_count(self) -> int:
        if self.total_results is None:
            return 0
        return math.ceil(self.total_results / self.items_per_page)
