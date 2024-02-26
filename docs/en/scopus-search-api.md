
# Scopus Search API

To search the articles and retrieve the information we need from them, we are using the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"}, which is one of the APIs made available by [Elsevier](https://www.elsevier.com/){:target="_blank"}. It is a search interface associated with the Scopus cluster, which contains Scopus abstracts.

To use the API we need to make a request to the API url and pass some parameters. Below are some details:

## Base Url

The Scopus Search API base url

```text
https://api.elsevier.com/content/search/scopus
```

## Query

As our search is based on keywords, we are using a query parameter with [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="_blank"} to specify our search method, which is `TITLE-ABS-KEY`, a combined field that will search for keywords in abstracts, keywords, and titles of articles.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

## Fields

To return only the information that interests us from the articles, we can specify some [Scopus Fields](https://dev.elsevier.com/sc_search_views.html){:target="_blank"} to filter the response.

```text
field=field1,field2,field3,...
```

## Date

The date range of interest for published articles.

```text
date=year1-year2
```

## Request Headers

The basic headers that we must include in the request. Remember to enter your `Api Key`.

```json
"X-ELS-APIKey": "Your Api Key",
"User-Agent": "Mozilla/5.0",
"Accept": "application/json",
"Content-Type": "application/json"
```

## Url

This is an example of a complete url with all the parameters we requested.

```text
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python AND Machine Learning)&field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier&date=2018-2024&suppressNavLinks=true
```

## Response Headers

After the search is complete, the API will return some information about the availability of using your `Api Key` in the response [Headers](https://dev.elsevier.com/api_key_settings.html){:target="_blank"}, so be sure to check it carefully, especially if you use the API for free as a part of an educational institution.

```json
"X-RateLimit-Limit": "Shows API quota setting",
"X-RateLimit-Remaining": "Shows API remaining quota",
"X-RateLimit-Reset": "Date/Time in Epoch seconds when API quota resets"
```
