from datetime import datetime

CURRENT_YEAR = datetime.now().year
LAST_THREE_YEARS = CURRENT_YEAR - 3
LAST_DECADE = CURRENT_YEAR - 10

BOOLEAN_OPERATOR = " AND "
NULL = "null"

QUOTA_EXCEEDED_CODE = "QUOTA_EXCEEDED"
RATE_LIMIT_EXCEEDED_CODE = "RATE_LIMIT_EXCEEDED"

URL_COLUMN = "Article Preview Page URL"
AUTHORS_COLUMN = "Authors"
TITLE_COLUMN = "Title"
DATE_COLUMN = "Date"

SEARCH_API_URL = (
    "https://api.elsevier.com/content/search/scopus?apiKey={apikey}&query="
    "TITLE-ABS-KEY({query})&field=dc:identifier&suppressNavLinks=true&date"
    "={date}&count={count}&sort=+pubyear,+coverDate,+relevancy"
)
PAGINATION_URL = "{search_url}&start={page}"
ABSTRACT_API_URL = "{abstract_url}?apiKey={apikey}&field={fields}"
ARTICLE_PAGE_URL = (
    "https://www.scopus.com/inward/record.uri"
    "?partnerID=HzOxMe3b&scp={scopus_id}&origin=inward"
)

FIELDS = (
    "dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby"
    "-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors"
)

HTTP_CODE_ERRORS = {
    400: "Invalid Request: invalid information submitted",
    401: (
        "Authentication Error: user cannot be authenticated"
        " due to missing/invalid credentials"
    ),
    403: (
        "Authorization/Entitlements Error: User cannot be "
        "authenticated or entitlements cannot be validated"
    ),
    429: (
        "Quota Exceeded: the requester has exceeded the "
        "quota limits associated with their API Key"
    ),
    500: "Generic Error: Scopus API back-end processing errors",
}

SCOPUS_HEADERS = {
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.scopus.com/",
    "Origin": "https://www.scopus.com",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Connection": "keep-alive",
}
