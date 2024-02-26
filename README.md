<!-- cSpell:disable -->
# Scopus Searcher API

<p align="center">
  <img src="./docs/images/favicon.png" width="300" alt="FastAPI">
</p>
<p align="center">
    <em>API for Bibliographic Survey of Scopus Articles</em>
</p>

---

**Documentation**: <http://>

**Swagger UI**: <http://127.0.0.1:8000>

**Web Application**: <http://127.0.0.1:8000/scopus-searcher/api>

---

## Definitions

This API was developed to facilitate the search for articles for research and the development of theoretical references for articles and final papers. It will use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl), maintained by the [Elsevier](https://www.elsevier.com/pt-br) company, to enable searches in the [Scopus](https://www.scopus.com/home.uri) cluster, which is the largest database of abstracts and citations of quality research literature and sources on the web.

To perform the search, you will need [Python3](https://www.python.org/) or [Docker](https://www.docker.com/) to be installed to run the application, you will also need to generate an `Api Key` and select a maximum of four `keywords` based on the topic of your search. Start the application, go to the web page or [Swagger](https://github.com/swagger-api/swagger-ui), and send the `Api Key` and your `keywords`, if any article is found successfully, it will return a [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values) containing all the information.

---

## Run

```bash
# Create Python Virtual Environment
$ make venv v=3.**

# Activate Venv
$ source .venv/bin/activate

# Install all the Dependencies
(.venv) $ make install

# Run App locally
(.venv) $ make run

# Run App in Docker
$ make docker
```

---

### API Key

You must obtain an `Api Key` to use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl) and search for articles. This key has no spaces and is made up of 32 characters containing only letters and numbers. It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/), clicking on the **I want an API Key** button and registering. If you are part of an educational institution, you can try to confirm if your institution is registered with [Elsevier](https://www.elsevier.com/pt-br) to sign in via your organization, or you can also try to register with your academic email.

### Keywords

Based on the theme or subject of your research, you must select a minimum of two and a maximum of four `keywords`, which will be used as parameters and filters when searching for articles in the API. They will be searched simultaneously in the title, abstract and keywords of the articles. Each `keyword` must be written in English, containing only letters, numbers, spaces and underscores, with a minimum of 2 and a maximum of 20 characters.
