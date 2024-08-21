from app.core.data.dtos import ScrapeData


def test_scrape_data():
    scrape_data = ScrapeData(0, "any", "any", "any")
    index, data = scrape_data.unpack()
    assert index == 0
    assert data == ["any", "any", "any"]
