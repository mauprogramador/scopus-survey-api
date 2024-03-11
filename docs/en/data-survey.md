# Data Survey

Taking into account that the objective of this application is to carry out a theoretical reference survey for research and as a basis for future academic work, we selected a group of specific information that will be consolidated from the search and scraping results to reference the articles.

Below is the mapping of the information fields:

| Field                 | Column           | Description                        |
| :-------------------- | :--------------- | :--------------------------------- |
| prism:publicationName | Publication Name | Source Title                       |
| prism:coverDate       | Date             | Publication Date                   |
| dc:identifier         | Scopus Id        | -                                  |
| prism:url             | URL              | Content Abstract Retrieval API URI |
| dc:title              | Title            | Article Title                      |
| prism:volume          | Volume           | -                                  |
| prism:doi             | DOI              | Document Object Identifier         |
| citedby-count         | Citations        | Cited-by Count                     |
| -                     | Authors          | Complete Author list               |
| -                     | Abstract         | Complete Abstract                  |

Except for the `Authors` and `Abstract` fields that were inserted later and populated with the scraping results, all other fields came from the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"} search results.

## Filtering

In order to provide greater consistency, all data went through three filtering steps:

- Firstly, all **exact repetitions** will be removed.
- Secondly, all results with the exact **same title** and **same authors** will be removed.
- Finally, all results with **similar titles** and from the **same authors** will be removed.

To perform the third step, we will [group](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html){:target="\_blank"} the articles based on the **author column**, so that if there are two or more articles with the exact same authors they will be grouped together. After that, we will use the [FuzzyWuzzy](https://pypi.org/project/fuzzywuzzy/){:target="\_blank"} library, which uses the [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance){:target="\_blank"}, to calculate the difference between titles, removing articles whose titles are at least `80%` similar.

!!! note

    If the last step is processed, a message will be displayed indicating the percentage of total articles loss.
