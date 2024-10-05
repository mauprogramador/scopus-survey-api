# Scopus Search API

We will use the [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"}, provided by [Elsevier]({{links.elsevier}}){:target="\_blank"}, to search for articles using the `Keywords` and obtain their **Scopus IDs**. It is a search interface associated with the **Scopus** cluster containing **Scopus abstracts**.

!!! info

    A [Cluster](https://en.wikipedia.org/wiki/Computer_cluster){:target="\_blank"} is a group of servers/computers that act like a single system.

## API Resource URL

We need to request the below {{abbr.url}} and pass some parameters to search.

```url
https://api.elsevier.com/content/search/scopus
```

## Query

Since our search is based on `Keywords`, we are using a query parameter with [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="\_blank"} to specify our search method, which is `TITLE-ABS-KEY`, a combined field that will search for `Keywords` in the abstracts, keywords, and titles of the articles.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

:material-information: Example with **Python** and **Machine Learning** as `Keywords`:

```text
query=TITLE-ABS-KEY(Python+AND+Machine+Learning)
```

## Fields

By specifying the [Scopus Fields](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"}, we can filter the response and get only the **Scopus IDs** of the articles.

```text
field=field1,field2,field3,...
```

:material-information: Example with the **field** used:

```text
field=dc:identifier
```

## Date Range

The **date range** of interest for published articles.

```text
date=year1-year2
```

:material-information: Example with **date range** used, is automatically set to the **last three years**:

```text
date=2021-2024
```

## Request Headers

The headers included in the request. One of them specifies your `API Key`.

```json
"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
"Accept-Encoding": "gzip, deflate, br",
"Referer": "https://www.scopus.com/",
"Origin": "https://www.scopus.com",
"Content-Type": "application/json",
"Accept": "application/json",
"User-Agent": "Mozilla/5.0",
"Connection": "keep-alive",
"X-ELS-APIKey": "Your API Key"
```

## Final URL

This is an example of a complete {{abbr.url}} with all the parameters we requested.

```url
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python+AND+Machine+Learning)&field=dc:identifier&date=2021-2024&suppressNavLinks=true
```

The parameter `suppressNavLinks` is used to suppress the inclusion of top-level navigation links in the response payload.

## Response Body

Example of a response body from the **Scopus Search API**.

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
        "dc:identifier": "SCOPUS_ID:85137995729"
      }
    ]
  }
}
```

| **Field**                 | **Description**                                                             |
| ------------------------- | --------------------------------------------------------------------------- |
| `search-results`          | Informs some metadata of the search operation and the articles found        |
| `opensearch:totalResults` | Total number of articles found                                              |
| `opensearch:startIndex`   | Index of the pagination from which we start to retrieve a group of articles |
| `opensearch:itemsPerPage` | Number of articles divided into each page, when there are many results      |
| `opensearch:Query`        | Some metadata about the submitted boolean search queries                    |
| `entry`                   | Lists of articles with the fields specified in the search                   |
