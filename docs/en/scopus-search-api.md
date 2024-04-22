# Scopus Search API

To search the articles and retrieve the information we need from them, we are using the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}, which is one of the APIs made available by [Elsevier](https://www.elsevier.com/){:target="\_blank"}. It is a search interface associated with the Scopus cluster, which contains Scopus abstracts.

To use the **API** we need to make a request to the **API** URL and pass some parameters. Below are some details:

## Base URL

The Scopus Search API base URL

```text
https://api.elsevier.com/content/search/scopus
```

## Query

As our search is based on keywords, we are using a query parameter with [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="\_blank"} to specify our search method, which is `TITLE-ABS-KEY`, a combined field that will search for keywords in abstracts, keywords, and titles of articles.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

Example with **Python** and **Machine Learning** as `Keywords`:

```text
query=TITLE-ABS-KEY(Python+AND+Machine+Learning)
```

## Fields

To return only the information that interests us from the articles, we can specify some [Scopus Fields](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"} to filter the response.

```text
field=field1,field2,field3,...
```

Example with all **fields** used:

```text
field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier
```

## Date

The date range of interest for published articles.

```text
date=year1-year2
```

Example with **date range** used, is automatically set to the **last three years**:

```text
date=2021-2024
```

## Request Headers

The basic headers that we must include in the request. Remember to enter your `Api Key`.

```json
"X-ELS-APIKey": "Your Api Key",
"User-Agent": "Mozilla/5.0",
"Accept": "application/json",
"Content-Type": "application/json"
```

## URL

This is an example of a complete URL with all the parameters we requested.

```text
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python+AND+Machine+Learning)&field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier&date=2021-2024&suppressNavLinks=true
```

The parameter **suppressNavLinks** is used to suppress the inclusion of top-level navigation links in the response payload.

## Response Headers

After the search is complete, the **API** will return some information about the availability of using your `Api Key` in the response [Headers](https://dev.elsevier.com/api_key_settings.html){:target="\_blank"}, so be sure to check it carefully, especially if you use the **API** for free as a part of an educational institution.

```json
"X-RateLimit-Limit": "Shows API request quota limit",
"X-RateLimit-Remaining": "Shows API remaining quota",
"X-RateLimit-Reset": "Date/Time in Epoch seconds when API quota resets"
```

## Response Body

The `search-results` field informs some parameters of the search results, such as the total results (`totalResults`) and the terms searched (`Query`). The `entry` field lists the results of the article fields.

```json
{
    "search-results": {
        "opensearch:totalResults": "1",
        "opensearch:startIndex": "0",
        "opensearch:itemsPerPage": "1",
        "opensearch:Query": {
            "@role": "request",
            "@searchTerms": "TITLE-ABS-KEY(Images, Machine Learning, Artificial Intelligence, Computer Vision)",
            "@startPage": "0"
        },
        "entry": [
            {
                "@_fa": "true",
                "prism:url": "https://api.elsevier.com/content/abstract/scopus_id/85137995729",
                "dc:identifier": "SCOPUS_ID:85137995729",
                "dc:title": "Real Time Facial Emotions Detection of Multiple Faces Using Deep Learning",
                "prism:publicationName": "Lecture Notes in Networks and Systems",
                "prism:volume": "475",
                "prism:coverDate": "2023-01-01",
                "prism:doi": "10.1007/978-981-19-2840-6_29",
                "citedby-count": "0"
            }
        ]
    }
}
```

## Reducing the Count

If you want, you can reduce the number of articles that will be returned by going to `app/gateway/api_config.py` and adding the **count** parameter in the **API_URL** attribute of the **ApiConfig** class, which is a numeric value representing the maximum number of results to be returned for the search.

```py title="api_config.py" linenums="1" hl_lines="5"
class ApiConfig:
    API_URL = (
        'https://api.elsevier.com/content/search/scopus'
        '?query=TITLE-ABS-KEY({query})&field={fields}&date={date}'
        '&suppressNavLinks=true&count=14'
    )
```
