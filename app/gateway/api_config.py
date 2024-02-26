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

    DATE_RANGE = '2018-2023'

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

    @classmethod
    def get_search_articles_url(cls, query: str) -> str:
        return cls.API_URL.format(
            query=query, fields=cls.FIELDS, date=cls.DATE_RANGE
        )

    @classmethod
    def get_article_page_url(cls, scopus_id: str) -> str:
        return cls.LINK_REF_SCOPUS.format(scopus_id=scopus_id)
