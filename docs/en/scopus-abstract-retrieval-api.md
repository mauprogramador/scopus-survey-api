# Scopus Abstract Retrieval API

After obtaining the **Scopus IDs** of the articles, the next step is to use them to retrieve all the information about each article. We will use the [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}, provided by [Elsevier]({{links.elsevier}}){:target="\_blank"}, to retrieve the **Scopus abstracts** with **rich article metadata** of all the articles.

!!! info

    In the old version `v2.0.0`, we web scraped the [Scopus article preview page](https://www.scopus.com/home.uri?zone=header&origin=recordpage){:target="\_blank"} using [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/){:target="\_blank"}, but we have now abandoned this practice.

## API Resource URL

We need to request the below {{abbr.url}} and pass some parameters to get the **Scopus abstract**.

```url
https://api.elsevier.com/content/abstract/scopus_id
```

## Scopus ID

To retrieve a **Scopus abstract** of a specific article, we need to set the `scopus_id` path parameter, which refers to a **unique Scopus identifier** assigned to each **Scopus article/abstract**.

```text
/{scopus_id}
```

:material-information: Example with **SCOPUS_ID:85197125619** as **Scopus ID**:

```text
/SCOPUS_ID:85197125619
```

## Fields

By specifying the [Scopus Fields](https://dev.elsevier.com/sc_abstract_retrieval_views.html){:target="\_blank"}, we can filter the response and get only the desired information of the articles.

```text
field=field1,field2,field3,...
```

:material-information: Example with all **fields** used:

```text
field=dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors
```

## Request Headers

The headers include in the request. One of them specifies your `API Key`.

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
"X-ELS-APIKey": "Your API Key",
```

## Final URL

This is an example of a complete {{abbr.url}} with all the parameters we requested.

```url
https://api.elsevier.com/content/abstract/scopus_id/SCOPUS_ID:85197125619&field=dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors
```

## Response Body

Example of a response body from the **Scopus Abstract Retrieval API** on an **institutional network**.

```json
"abstracts-retrieval-response": {
    "coredata": {
        "eid": "2-s2.0-85197125619",
        "citedby-count": "0",
        "prism:volume": "14",
        "dc:description": "The advancement of technology has significantly transformed the livestock [...]",
        "prism:coverDate": "2024-06-01",
        "dc:title": "Digital and Precision Technologies in Dairy Cattle Farming: A Bibliometric Analysis",
        "dc:creator": {
            "author": [
                {
                    "ce:given-name": "Franck Morais",
                    "preferred-name": {
                        "ce:given-name": "Franck Morais",
                        "ce:initials": "F.M.",
                        "ce:surname": "de Oliveira",
                        "ce:indexed-name": "de Oliveira F.M."
                    },
                    "@seq": "1",
                    "ce:initials": "F.M.",
                    "@_fa": "true",
                    "affiliation": {
                        "@id": "60017841",
                        "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                    },
                    "ce:surname": "de Oliveira",
                    "@auid": "57275191700",
                    "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                    "ce:indexed-name": "de Oliveira F.M."
                }
            ]
        },
        "prism:doi": "10.3390/ani14121832",
        "publishercopyright": "© 2024 by the authors.",
        "prism:publicationName": "Animals",
        "dc:identifier": "SCOPUS_ID:85197125619"
    },
    "authors": {
        "author": [
            {
                "ce:given-name": "Franck Morais",
                "preferred-name": {
                    "ce:given-name": "Franck Morais",
                    "ce:initials": "F.M.",
                    "ce:surname": "de Oliveira",
                    "ce:indexed-name": "de Oliveira F.M."
                },
                "@seq": "1",
                "ce:initials": "F.M.",
                "@_fa": "true",
                "affiliation": {
                    "@id": "60017841",
                    "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                },
                "ce:surname": "de Oliveira",
                "@auid": "57275191700",
                "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                "ce:indexed-name": "de Oliveira F.M."
            }
        ]
    }
}
```

| **Field**                      | **Description**                                             |
| ------------------------------ | ----------------------------------------------------------- |
| `abstracts-retrieval-response` | Lists article's rich metadata                               |
| `coredata`                     | Lists the article's core metadata with the specified fields |
| `authors`                      | Lists all authors of the article                            |
| `author`                       | Lists the data of all authors of the article                |

Example of a response body from the **Scopus Abstract Retrieval API** on an **off-campus network**.

```json
"abstracts-retrieval-response": {
    "coredata": {
        "eid": "2-s2.0-85197125619",
        "citedby-count": "0",
        "prism:volume": "14",
        "prism:coverDate": "2024-06-01",
        "dc:title": "Digital and Precision Technologies in Dairy Cattle Farming: A Bibliometric Analysis",
        "dc:creator": {
            "author": [
                {
                    "ce:given-name": "Franck Morais",
                    "preferred-name": {
                        "ce:given-name": "Franck Morais",
                        "ce:initials": "F.M.",
                        "ce:surname": "de Oliveira",
                        "ce:indexed-name": "de Oliveira F.M."
                    },
                    "@seq": "1",
                    "ce:initials": "F.M.",
                    "@_fa": "true",
                    "affiliation": {
                        "@id": "60017841",
                        "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                    },
                    "ce:surname": "de Oliveira",
                    "@auid": "57275191700",
                    "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                    "ce:indexed-name": "de Oliveira F.M."
                }
            ]
        },
        "prism:doi": "10.3390/ani14121832",
        "publishercopyright": "© 2024 by the authors.",
        "prism:publicationName": "Animals",
        "dc:identifier": "SCOPUS_ID:85197125619"
    }
}
```

| **Field**                      | **Description**                                             |
| ------------------------------ | ----------------------------------------------------------- |
| `abstracts-retrieval-response` | Lists article's rich metadata                               |
| `coredata`                     | Lists the article's core metadata with the specified fields |
| `author`                       | Lists the data of the first author of the article           |
