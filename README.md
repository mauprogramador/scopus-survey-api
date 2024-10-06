# Scopus Searcher API

<p align="center">
  <img src="./docs/assets/img/favicon.png" width="300" alt="Logo">
</p>
<p align="center">
  <em>Web API for Bibliographic Survey of Scopus Articles</em>
</p>
<p align="center">
  <a href="https://github.com/mauprogramador/scopus-searcher-api/actions/workflows/verification.yml" target="_blank" rel="external" title="Linting and Testing Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/verification.yml?branch=master&event=push&logo=github&label=Lint | Test&color=FF5722" alt="Linting and Testing Action">
  </a>
  <a href="https://github.com/mauprogramador/scopus-searcher-api/actions/workflows/documentation.yml" target="_blank" rel="external" title="Documentation Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=2196F3" alt="Documentation Action">
  </a>
  <img src="https://img.shields.io/badge/Coverage-99%25-4CAF50" alt="Coverage" title="Coverage">
  <a href="https://github.com/mauprogramador/scopus-searcher-api/releases/tag/v3.0.0" target="_blank" rel="external" title="Web API Version">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-searcher-api?logo=github&label=Web API Version&color=E9711C" alt="Web API Version">
  </a>
  <a href="https://www.python.org/" target="_blank" rel="external" title="Python3 Version">
    <img src="https://img.shields.io/badge/Python-v3.11-3776AB?logo=python&logoColor=FFF" alt="Python3 Version">
  </a>
</p>

---

Federal Institute of Mato Grosso do Sul - <a href="https://www.ifms.edu.br/campi/campus-tres-lagoas" target="_blank" rel="external" title="IFMS - Campus Três Lagoas">IFMS - Campus Três Lagoas</a><br/>
Technology in Systems Analysis and Development - <a href="https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas" target="_blank" rel="external" title="TADS">TADS</a><br/>

**Documentation**: <a href="https://mauprogramador.github.io/scopus-searcher-api/" target="_blank" rel="external" title="Documentation">https://mauprogramador.github.io/scopus-searcher-api/</a>

**Swagger UI**: <a href="http://127.0.0.1:8000" target="_blank" rel="external" title="Swagger UI">http://127.0.0.1:8000</a>

**Web API**: <a href="http://127.0.0.1:8000/scopus-searcher/api" target="_blank" rel="external" title="Web API">http://127.0.0.1:8000/scopus-searcher/api</a>

---

## Overview

This **Web API** was developed to facilitate the search for articles for research and the development of theoretical references. It will use both the <a href="https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl" target="_blank" rel="external" title="Scopus Search API Documentation">Scopus Search API</a> and the <a href="https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl" target="_blank" rel="external" title="Scopus Abstract Retrieval API Documentation">Scopus Abstract Retrieval API</a>, maintained by the <a href="https://www.elsevier.com" target="_blank" rel="external" title="Elsevier website">Elsevier</a> company, to query the <a href="https://www.scopus.com/home.uri" target="_blank" rel="external" title="Scopus website">Scopus</a> cluster, which is the largest database of abstracts and citations of quality research literature and sources on the web.

To perform the search, you will need <a href="https://www.python.org/downloads/release/python-3117/" target="_blank" rel="external" title="Python3.11">Python3 `v3.11`</a> or <a href="https://www.docker.com/" target="_blank" rel="external" title="Docker">Docker</a> installed to run the application, you will also need to generate an `API Key` and **select a maximum of four** `Keywords` based on the topic of your search. Start the application, go to the web page, submit your `API Key` and your `Keywords`, and if any articles are found, a <abbr title="Comma-Separated Values">**CSV**</abbr> file with the article information will be returned.

---

## Run locally with Poetry

```bash
# Setup Venv
make setup

# Activate Venv
source .venv/bin/activate

# Install dependencies
(.venv) make install

# Run the App locally
(.venv) make run
```

## Run locally with Pip

```bash
# Setup Venv
make setup

# Activate Venv
source .venv/bin/activate

# Install dependencies
(.venv) pip3 install -r requirements/requirements.txt

# Run the App locally
(.venv) make run
```

## Run in Docker

```bash
# Run the App in Docker Container
make docker
```

---

### API Key

You must obtain an `API Key` to access the <a href="https://dev.elsevier.com/sc_apis.html" target="_blank" rel="external" title="Scopus APIs">Scopus APIs</a> to search and retrieve the articles' information. It **has no spaces** and is **made up of 32 characters** containing **only letters and numbers**. It can be obtained by accessing the <a href="https://dev.elsevier.com/" target="_blank" rel="external" title="Elsevier Developer Portal">Elsevier Developer Portal</a>, clicking on the **I want an API Key** button and registering.

If you are part of an educational institution, you can try to confirm if your institution is registered with <a href="https://www.elsevier.com" target="_blank" rel="external" title="Elsevier website">Elsevier</a> to sign in via your organization, or you can also try to register with your academic email.

### Keywords

Based on the theme or subject of your research, you must select a **minimum of two** and a **maximum of four `Keywords`**, which will be used as parameters and filters in the simultaneous search in the title, abstract and keywords of the articles. Each `Keyword` must be **written in English**, containing **only letters, numbers, spaces and underscores**, with a **minimum of 2** and a **maximum of 50 characters**.

### Institutional Network

Please be aware that the `API Key` will only authenticate correctly if you submit it while inside your **university/institution's network**, and this does not include <abbr title="Virtual Private Network">**VPN**</abbr> or <abbr title="Intermediary server application between the client and the server">**proxy**</abbr> access. Therefore, if you are **fully remote** and **off-campus**, the **abstract** and **all authors** of the articles will **not be returned**.

---

## Example

The table below exemplifies the results of a search. Using **Computer Vision**, **Scopus** and **Machine Learning** as `Keywords`, a total of **71** articles were found. There was no [loss due to similarity](./docs/en/api-limit-and-fields-and-filter.md#filtering-results) and it took around **18704.65ms**.

![Table Result](./docs/assets/img/table-result-en.png "Table Result")

<a href="./docs/assets/data/example.csv" download="example.csv">Click here</a> to download the <abbr title="Comma-Separated Values">**CSV**</abbr> file for the survey example above.

---

This project is licensed under the terms of the [MIT license](./docs/en/license.md)
