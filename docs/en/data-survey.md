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

Except for the `Authors` and `Abstract` fields that were inserted later and populated with the scraping results, all other fields came from the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"} search results.
The data will be filtered, firstly by removing exact repetitions and secondly by removing results with the same title and same authors.
