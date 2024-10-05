# Scopus Searcher API

<figure markdown="span">
  ![Logo](../assets/img/logo.png "Scopus Searcher API Logo"){ width="300" }
  <figcaption>Web API for Bibliographic Survey of Scopus Articles</figcaption>
</figure>
<p align="center">
  <a href="{{links.workflows}}/verification.yml" target="_blank" title="Linting and Testing Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/verification.yml?branch=master&event=push&logo=github&label=Lint | Test&color=FF5722" alt="Linting and Testing Action">
  </a>
  <a href="{{links.workflows}}/documentation.yml" target="_blank" title="Documentation Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=2196F3" alt="Documentation Action">
  </a>
  <img src="https://img.shields.io/badge/Coverage-99%25-4CAF50" alt="Coverage" title="Coverage">
  <a href="{{links.releases}}/v2.0.0" target="_blank" title="API Version">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-searcher-api?logo=github&label=API Version&color=E9711C" alt="API Version">
  </a>
  <a href="https://www.python.org/" target="_blank" title="Python3 Version">
    <img src="https://img.shields.io/badge/Python-v3.11-3776AB?logo=python&logoColor=FFF" alt="Python3 Version">
  </a>
</p>

---

Federal Institute of Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas){:target="\_blank"} <br/>
Technology in Systems Analysis and Development - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas){:target="\_blank"} <br/>
Brazil - MS - Três Lagoas <br/>

**Source Code:** <{{links.repository}}>{:target="\_blank"}

---

## Overview

This application was developed to facilitate the search for articles for research and the development of theoretical references. It will use both the [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"} and the [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}, maintained by the [Elsevier]({{links.elsevier}}){:target="\_blank"} company, to query the [Scopus](https://www.scopus.com/home.uri){:target="\_blank"} cluster, which is the largest database of abstracts and citations of quality research literature and sources on the web.

To perform the search, you will need to have [Python3]({{links.python}}){:target="\_blank"} or [Docker](https://www.docker.com/){:target="\_blank"} installed to run the application, you will also need to generate an `API Key` and **select a maximum of four** `Keywords` based on the topic of your search. Start the application, go to the web page, submit your `API Key` and your `Keywords`, and if any articles are found, a {{abbr.csv}} file with the article information will be returned.

!!! note

    This project is licensed under the terms of the [MIT license](./license.md).
