from pandas import DataFrame

from app.core.common.types import Articles
from app.core.config.scopus import (
    ARTICLE_PAGE_URL,
    AUTHORS_COLUMN,
    SCOPUS_ID_COLUMN,
    TEMPLATE_COLUMN,
    TITLE_COLUMN,
    URL_COLUMN,
)
from tests.helpers.models import Response


def article(title: str = None, doi: str = None) -> dict[str, str]:
    return {
        "@_fa": "true",
        "prism:url": "any",
        "dc:identifier": "SCOPUS_ID:any",
        "dc:title": title if title else "any",
        "prism:publicationName": "any",
        "prism:volume": "any",
        "prism:coverDate": "any",
        "prism:doi": doi if doi else "any",
        "citedby-count": "any",
    }


def no_link_article(title: str = None, doi: str = None) -> dict[str, str]:
    return {
        "prism:url": "any",
        "dc:identifier": "SCOPUS_ID:any",
        "dc:title": title if title else "any",
        "prism:publicationName": "any",
        "prism:volume": "any",
        "prism:coverDate": "any",
        "prism:doi": doi if doi else "any",
        "citedby-count": "any",
    }


def pagination(entry: Articles) -> list[Response]:
    total = (len(entry) * 25) - 1
    return [Response(scopus_json(total, [article])) for article in entry]


def scopus_json(total: int, entry: Articles) -> dict:
    return {
        "search-results": {
            "opensearch:totalResults": total,
            "opensearch:itemsPerPage": 25,
            "entry": entry,
        }
    }


def article_page_subsets() -> tuple[DataFrame, DataFrame]:
    ids_rows, any_rows = ["any:any"] * 7, ["any"] * 7
    data = {SCOPUS_ID_COLUMN: ids_rows, URL_COLUMN: any_rows}
    df_in = DataFrame(data.copy())
    data[URL_COLUMN] = [ARTICLE_PAGE_URL.format(scopus_id="any")] * 7
    data[TEMPLATE_COLUMN] = any_rows
    return df_in, DataFrame(data)


def authors_tags(authors_names: list[str]) -> str:
    return "\n".join(
        [
            f'<li><span class="previewTxt">{name}</span></li>'
            for name in authors_names
        ]
    )


def template(authors: list[str] = None, abstract: str = None) -> str:
    authors = authors if authors else ["any1, A.", "any2, B."]
    abstract = abstract if abstract else "any    \nabstract"
    return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Article Page</title>
        </head>
        <body>
            <section id="authorlist">
            <ul class="list-inline">
                {authors_tags(authors)}
            </ul>
            </section>
            <section id="abstractSection">
                <p>{abstract}</p>
            </section>
        </body>
        </html>
    """


def scrap_subset(template_column: str | list[str]) -> DataFrame:
    if isinstance(template_column, str):
        data = [{URL_COLUMN: "any", TEMPLATE_COLUMN: template_column}]
    else:
        data = [
            {URL_COLUMN: "any", TEMPLATE_COLUMN: template}
            for template in template_column
        ]
    return DataFrame(data)


def similar_data(similar: bool, context: dict[str, int]) -> DataFrame:
    data: list[dict[str, str]] = []
    for key, value in context.items():
        for index in range(value):
            title = f"{key}any{value}-{index+1}" if similar else str(index)
            data.append({AUTHORS_COLUMN: key, TITLE_COLUMN: title})
    return DataFrame(data)


def similar_articles(
    similar: bool | tuple[bool, bool], context: dict[str, int]
) -> list[Response]:
    total = sum(context.values())
    similar = (similar, similar) if isinstance(similar, bool) else similar
    articles: list[dict[str, str]] = []
    templates: list[Response] = []
    for key, value in context.items():
        for index in range(value):
            title = f"any{value}-{index+1}" if similar[0] else str(index)
            articles.append(article(f"{key}{title}"))
            authors = [key] if similar[1] else [f"any{index}, {key}."]
            templates.append(Response(template(authors)))
    return [Response(scopus_json(total, articles)), *templates]
