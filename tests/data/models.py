from json import dumps

from pydantic import BaseModel, Field


class FakeResponse:
    def __init__(self, content: dict | str = None, status_code: int = None):
        if content or (isinstance(content, str) and len(content) == 0):
            self.text = content if isinstance(content, str) else dumps(content)
        self.status_code = status_code if status_code else 200


class Article(BaseModel):
    link: bool = Field(serialization_alias='@_fa', default=True)
    url: str = Field(serialization_alias='prism:url', default='any')
    volume: str = Field(serialization_alias='prism:volume', default='any')
    date: str = Field(serialization_alias='prism:coverDate', default='any')
    doi: str = Field(serialization_alias='prism:doi', default='any')
    citations: str = Field(serialization_alias='citedby-count', default='any')
    title: str = Field(serialization_alias='dc:title', default='any')
    scopus_id: str = Field(
        serialization_alias='dc:identifier', default='SCOPUS_ID:12345'
    )
    publication_name: str = Field(
        serialization_alias='prism:publicationName', default='any'
    )
