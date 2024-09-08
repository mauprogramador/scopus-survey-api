class ScrapeData:
    """DTO to transfer the scraped data"""

    def __init__(
        self, index: int, url: str, authors_names: str, abstract: str
    ) -> None:
        """DTO to transfer the scraped data"""
        self.index = index
        self.data = [str(url), authors_names, abstract]

    def get_values(self) -> tuple[int, list[str]]:
        return self.index, self.data
