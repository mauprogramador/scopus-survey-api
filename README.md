<!-- cSpell:disable -->
# Scopus Searcher API

<p align="center">
  <img src="./docs/images/favicon.png" width="300" alt="FastAPI">
</p>
<p align="center">
  <em>API for Bibliographic Survey of Scopus Articles</em>
</p>
<p align="center">
  <a href="https://github.com/mauprogramador/scopus-searcher-api/actions/workflows/verification.yml" target="_blank">
    <img alt="Linting and Testing Action" src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/verification.yml?branch=master&event=push&logo=github&label=Lint | Test&color=C7D41B">
  </a>
  <a href="https://github.com/mauprogramador/scopus-searcher-api/actions/workflows/documentation.yml" target="_blank">
    <img alt="Documentation Action" src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=4CA9E8">
  </a>
  <img src="https://img.shields.io/badge/Coverage-99%25-81CC2B" alt="Coverage">
  <a href="https://github.com/mauprogramador/scopus-searcher-api/releases/tag/v2.0.0" target="_blank">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-searcher-api?logo=github&label=API Version&color=E9711C" alt="API Version">
  </a>
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/Python-v3.11-3776AB?logo=python&logoColor=FFF" alt="Python Version">
  </a>
</p>
<!-- <img src="https://github.com/mauprogramador/scopus-searcher-api/workflows/Documentation/badge.svg?event=push&branch=master" alt="Linting and Testing">
<img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fmauprogramador%2Fscopus-searcher-api%2Fmaster%2Fpyproject.toml"> -->

---

**Documentation**: <https://mauprogramador.github.io/scopus-searcher-api/>

**Swagger UI**: <http://127.0.0.1:8000>

**Web Application**: <http://127.0.0.1:8000/scopus-searcher/api>

---

## Definitions

This API was developed to facilitate the search for articles for research and the development of theoretical references for articles and final papers. It will use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl), maintained by the [Elsevier](https://www.elsevier.com/pt-br) company, to enable searches in the [Scopus](https://www.scopus.com/home.uri) cluster, which is the largest database of abstracts and citations of quality research literature and sources on the web.

To perform the search, you will need [Python3.11](https://www.python.org/) or [Docker](https://www.docker.com/) to be installed to run the application, you will also need to generate an `Api Key` and select a maximum of four `keywords` based on the topic of your search. Start the application, go to the web page or [Swagger](https://github.com/swagger-api/swagger-ui), and send the `Api Key` and your `keywords`, if any article is found successfully, it will return a [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values) containing all the information.

---

## Run Locally

```bash
# Create Python Virtual Environment
make venv v=3.11

# Activate Venv
source .venv/bin/activate

# Install all the Dependencies
(.venv) $ make install

# Run App locally
(.venv) $ make run
```

## Run in Docker

```bash
# Run App in Docker
make docker
```

---

### API Key

You must obtain an `Api Key` to use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl) and search for articles. This key has no spaces and is made up of 32 characters containing only letters and numbers. It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/), clicking on the **I want an API Key** button and registering. If you are part of an educational institution, you can try to confirm if your institution is registered with [Elsevier](https://www.elsevier.com/pt-br) to sign in via your organization, or you can also try to register with your academic email.

### Keywords

Based on the theme or subject of your research, you must select a minimum of two and a maximum of four `keywords`, which will be used as parameters and filters when searching for articles in the API. They will be searched simultaneously in the title, abstract and keywords of the articles. Each `keyword` must be written in English, containing only letters, numbers, spaces and underscores, with a minimum of 2 and a maximum of 20 characters.

---

## Example

The table below exemplifies the results of a search. Using **Python** and **Machine Learning** as `Keywords`, a total of **6786** articles were returned from the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl). To avoid time-consuming processing, we reduced the total to just **14**, there was no [loss due to similarity](https://mauprogramador.github.io/scopus-searcher-api/en/data-survey/#filtering) and it took around **34,012.64ms**.

![Web Table](./docs/images/csv-table.png)

<a href="./docs/example.csv" download="example.csv">Click here</a> to download the CSV file for the survey example above.
