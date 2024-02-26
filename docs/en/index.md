# Scopus Searcher API

Federal Institute of Mato Grosso do Sul ([IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas){:target="_blank"}) <br/>
Technology in Systems Analysis and Development ([TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas){:target="_blank"}) <br/>
Brazil - MS - Três Lagoas - February 14, 2024<br/>

**API for Bibliographic Survey of Scopus Articles** <br/>

**Source Code:** <https://github.com/mauprogramador/>{:target="_blank"}

---

## Overview

This API was developed to facilitate the search for articles for research and the development of theoretical references for articles and final papers. It will use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"}, maintained by the [Elsevier](https://www.elsevier.com/pt-br){:target="_blank"} company, to enable searches in the [Scopus](https://www.scopus.com/home.uri){:target="_blank"} cluster, which is the largest database of abstracts and citations of quality research literature and sources on the web.

To perform the search, you will need [Python3](https://www.python.org/){:target="_blank"} or [Docker](https://www.docker.com/){:target="_blank"} to be installed to run the application, you will also need to generate an `Api Key` and select a maximum of four `keywords` based on the topic of your search. Start the application, go to the web page or [Swagger](https://github.com/swagger-api/swagger-ui){:target="_blank"}, and send the `Api Key` and your `keywords`, if any article is found successfully, it will return a [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="_blank"} containing all the information.
