from app.core.data.dtos import ScrapeData


def test_scrape_data():
    scrape_data = ScrapeData(0, "any", "any", "any")
    index, data = scrape_data.get_values()
    assert index == 0
    assert data == ["any", "any", "any"]
