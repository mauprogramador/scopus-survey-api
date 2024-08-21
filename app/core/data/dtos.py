class ScrapeData:
    """DTO to transfer the scraped data"""

    def __init__(self, index: int, *args: str) -> None:
        """DTO to transfer the scraped data"""
        self.index = index
        self.data = list(args)

    def unpack(self) -> tuple[int, list[str]]:
        return self.index, self.data
