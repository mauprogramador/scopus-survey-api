from pydantic import BaseModel, Field, model_validator

from app.core.interfaces import Gateway


class ScopusResponse(BaseModel):
    total_results: int = Field(validation_alias='opensearch:totalResults')
    items_per_page: int = Field(validation_alias='opensearch:itemsPerPage')
    entry: Gateway.SearchType = Field()

    @property
    def count(self) -> int:
        return int(self.total_results / self.items_per_page) + 1

    @model_validator(mode='before')
    @classmethod
    def flatten_json(cls, data: dict) -> dict:
        return data['search-results']
