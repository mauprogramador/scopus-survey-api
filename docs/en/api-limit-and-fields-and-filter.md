# APIs Limit & Fields & Filter

## APIs Limit

There is a limit to how many requests you can make to [Scopus {{abbr.api}}s]({{links.scApis}}){:target="\_blank"} using your `API Key`. After each request, the {{abbr.api}} will return some information about the availability of your `API Key` in the response [headers]({{links.scApiKey}}){:target="\_blank"}. This quota limit **resets every seven days**.

```json
"X-RateLimit-Limit": "Shows API request quota limit",
"X-RateLimit-Remaining": "Shows API remaining request quota",
"X-RateLimit-Reset": "Date/Time in Epoch seconds when API quota resets"
```

!!! info

    [Epoch](https://en.wikipedia.org/wiki/Epoch_(computing)){:target="\_blank"} is the number of seconds that have elapsed since January 1, 1970, also known as [Unix time](https://en.wikipedia.org/wiki/Unix_time){:target="\_blank"}.

## Quota Exceeded

If the **request quota** or {{abbr.throttling}} **rate** of the {{abbr.api}} is exceeded, you will receive an {{abbr.http}} status error [429: Too Many Requests]({{links.mdnStatus}}/429){:target="\_blank"}.

```json
"X-ELS-Status": "QUOTA_EXCEEDED - Quota Exceeded"
```

!!! note

    Learn more about the [quota of how much data an `API Key` can retrieve]({{links.scApiKey}}){:target="\_blank"}.

## Fields Mapping

Taking into account that the objective of this application is to carry out a survey of theoretical references for research and as a basis for future academic work, we selected a **group** of **specific information** from the **articles' metadata**.

| **Field**                 | **Column**               | **Description**                               |
| ------------------------- | ------------------------ | --------------------------------------------- |
| `link ref=scopus`         | Article Preview Page URL | Scopus article preview page URL               |
| `dc:identifier`           | Scopus ID                | Article Scopus ID                             |
| `authors` or `dc:creator` | Authors                  | Complete author list or only the first author |
| `dc:title`                | Title                    | Article title                                 |
| `prism:publicationName`   | Publication Name         | Source title                                  |
| `dc:description`          | Abstract                 | Article complete abstract                     |
| `prism:coverDate`         | Date                     | Publication date                              |
| `eid`                     | Electronic ID            | Article Electronic ID                         |
| `prism:doi`               | DOI                      | Document Object Identifier                    |
| `prism:volume`            | Volume                   | Identifier for a serial publication           |
| `citedby-count`           | Citations                | Cited-by count                                |

!!! note

    See an example of a [Scopus article preview page](https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=0037368024&origin=inward){:target="\_blank"}.

## Filtering Results

To provide greater consistency, all data goes through three filtering steps:

**1.** Firstly, all **exact repetitions** will be removed.<br>

**2.** Secondly, all results with the exact **same title** and **same authors** will be removed.<br>

**3.** Finally, all results with **similar titles** and from the **same authors** will be removed.

To perform the third step, we will [select](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html){:target="\_blank"} two or more articles that have exactly the **same authors**. After that, we will use the [TheFuzz](https://github.com/seatgeek/thefuzz){:target="\_blank"} library, which uses [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance){:target="\_blank"}, to calculate the **similarity between the titles** of the articles of those repeated authors and, finally, we will remove the articles whose titles are **at least `80%` similar**.

Articles that do not have **repeated authors** or **similar titles** will be disregarded. A **log** message will be displayed indicating the percentage of total loss of articles.
