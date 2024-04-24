from app.core.config import CURRENT_YEAR


class ApiConfig:
    API_URL = (
        'https://api.elsevier.com/content/search/scopus'
        '?query=TITLE-ABS-KEY({query})&field={fields}&date={date}'
        '&suppressNavLinks=true'
    )

    FIELDS = (
        'prism:coverDate,prism:url,prism:publicationName,'
        'citedby-count,prism:volume,dc:title,prism:doi,dc:identifier'
    )

    DATE_RANGE = f'{CURRENT_YEAR - 3}-{CURRENT_YEAR}'

    LINK_REF_SCOPUS = (
        'https://www.scopus.com/inward/record.uri'
        '?partnerID=HzOxMe3b&scp={scopus_id}&origin=inward'
    )

    RESPONSES = {
        400: 'Invalid information submitted',
        401: 'Authentication error: missing or invalid credentials',
        403: 'Authentication error: user cannot be validated',
        429: 'API key request quota limits exceeded',
        500: 'Internal error from Scopus API response',
    }

    MAPPINGS = {
        'prism:publicationName': 'Publication Name',
        'prism:coverDate': 'Date',
        'dc:identifier': 'Scopus Id',
        'prism:url': 'URL',
        'dc:title': 'Title',
        'prism:volume': 'Volume',
        'prism:doi': 'DOI',
        'citedby-count': 'Citations',
    }

    TEMPLATE = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <title>Article Page</title>
        </head>
        <body>
            <section id="authorlist">
            <ul class="list-inline">
                <li><span class="previewTxt">Any Author</span></li>
            </ul>
            </section>
            <section id="abstractSection">
                <p>Any Abstract</p>
            </section>
        </body>
        </html>
    """

    PAGE_HEADERS = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.scopus.com/',
        'Connection': 'keep-alive',
        'Content-Type': 'text/plain',
        'Origin': 'https://www.scopus.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9'
            ',image/avif,image/webp,image/apng,*/*;q=0.8,application/'
            'signed-exchange;v=b3;q=0.7'
        ),
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ),
    }

    @classmethod
    def get_search_articles_url(cls, query: str) -> str:
        return cls.API_URL.format(
            query=query, fields=cls.FIELDS, date=cls.DATE_RANGE
        )

    @classmethod
    def get_article_page_url(cls, scopus_id: str) -> str:
        return cls.LINK_REF_SCOPUS.format(scopus_id=scopus_id)

    @classmethod
    def get_api_headers(cls, api_key: str) -> dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'X-ELS-APIKey': api_key,
        }
