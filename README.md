# Scopus Survey API

<p align="center">
  <img src="./docs/assets/img/logo.png" width="250" alt="Logo">
  <img src="./web/static/img/ifms.ico" width="16" alt="IFMS">
  <img src="./web/static/img/scopus.ico" width="16" alt="Scopus">
</p>
<p align="center">
  <em>Web API for bibliographic survey of Scopus articles</em>
</p>
<p align="center">
  <a href="https://github.com/mauprogramador/scopus-survey-api/actions/workflows/verification.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-survey-api/verification.yml?branch=master&event=push&logo=github&label=Lint%26Test&color=C5362B" alt="Lint & Test">
  </a>
  <a href="https://github.com/mauprogramador/scopus-survey-api/actions/workflows/documentation.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-survey-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=2196F3" alt="Documentation">
  </a>
  <img src="https://img.shields.io/badge/Coverage-99%25-4CAF50" alt="Coverage">
  <a href="https://github.com/mauprogramador/scopus-survey-api/releases/latest">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-survey-api?logo=github&label=Release&color=E9711C" alt="Latest Release">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-v3.12-FBDA4E?logo=python&logoColor=FFF&labelColor=3776AB" alt="Python3 version">
  </a>
</p>
<p align="center">
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=FFF" alt="FastAPI">
  </a>
  <a href="https://docs.pydantic.dev/latest/">
    <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=FFF" alt="Pydantic">
  </a>
  <a href="https://pandas.pydata.org/docs/">
    <img src="https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=FFF" alt="Pandas">
  </a>
  <a href="https://docs.aiohttp.org/en/stable/">
    <img src="https://img.shields.io/badge/AIOHTTP-2C5BB4?logo=aiohttp&logoColor=FFF" alt="AIOHTTP">
  </a>
  <a href="https://getbootstrap.com/docs/5.3/getting-started/introduction/">
    <img src="https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=FFF" alt="Bootstrap">
  </a>
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/Poetry-60A5FA?logo=poetry&logoColor=FFF" alt="Poetry">
  </a>
  <a href="https://docs.pytest.org/en/stable/">
    <img src="https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=FFF" alt="Pytest">
  </a>
  <a href="https://www.mkdocs.org/">
    <img src="https://img.shields.io/badge/MkDocs-526CFE?logo=materialformkdocs&logoColor=FFF" alt="MkDocs">
  </a>
</p>
<p align="center">
  <a href="https://black.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/code style-black-000" alt="Black">
  </a>
  <a href="https://mypy.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/mypy-checked-2A6DB2" alt="MyPy">
  </a>
  <a href="https://pylint.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" alt="Pylint">
  </a>
  <a href="https://bandit.readthedocs.io/en/latest/">
    <img src="https://img.shields.io/badge/security-bandit-yellow" alt="Bandit">
  </a>
  <a href="https://bandit.readthedocs.io/en/latest/">
    <img src="https://img.shields.io/badge/audit-pip audit-3775A9" alt="Pip-Audit">
  </a>
</p>

---

Federal Institute of Mato Grosso do Sul &nbsp;&#8226;&nbsp; [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)
<br/>
Technology in Systems Analysis and Development &nbsp;&#8226;&nbsp; [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)
<br/>
Data provided by [Scopus](https://www.scopus.com)® &nbsp;&#8226;&nbsp; [Elsevier](https://www.elsevier.com)

- Documentation: <https://mauprogramador.github.io/scopus-survey-api/>
- Web API: <http://127.0.0.1:8000/v2/scopus-survey/en-US/search-articles>
- Swagger UI: <http://127.0.0.1:8000/>

---

## Overview

This a **web** <abbr title="Application Programming Interface">**API**</abbr> is designed to facilitate the **survey of information from academic documents** that will be used as high-quality literature sources on the web for research, bibliographic references, and [systematic reviews](https://en.wikipedia.org/wiki/Systematic_review). It is primarily intended for free, [non-commercial academic use](https://dev.elsevier.com/academic_research_scopus.html) by **students**, thus **improving accessibility**.

Through a web form, the application aims to enable a **personalized survey**, by first using the **API key**, **keywords**, and other **search parameters** submitted by the user to query [Scopus's vast database](https://www.elsevier.com/products/scopus) of high-quality abstract and citation sources, using the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl) and the [Scopus Abstract Retrieval API](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl), maintained by [Elsevier](https://www.elsevier.com).

Finally, all document data will be **systematically downloaded and gathered**, then validated, processed, and refined based on content similarity, removing duplicates and filtering similar documents, leaving only the **most relevant and recent data**, which will be organized and returned in a <abbr title="Comma-separated Values">**CSV**</abbr> **file**, allowing you to use the documents as you wish, depending on your circumstances.

---

## Configuration

Create an `.env` file to configure the following options:

| **Parameter**  | **Description**                                          | **Default** |
| -------------- | -------------------------------------------------------- | ----------- |
| `HOST`         | Sets the host address to listen on                       | `127.0.0.1` |
| `PORT`         | Sets the server port on which the application will run   | `8000`      |
| `RELOAD`       | Enable auto-reload on file changes for local development | `false`     |
| `WORKERS`      | Sets multiple worker processes                           | `1`         |
| `LOGGING_FILE` | Enable saving logs to files                              | `false`     |
| `DEBUG`        | Enable the debug mode and debug logs                     | `false`     |
| `PROGRESS_BAR` | Displays the progress bar of the request process         | `true`      |

- The `RELOAD` and `WORKERS` options are **mutually exclusive**.

- Setting the `HOST` to `0.0.0.0` makes the application externally available.

> [!NOTE]
> The address `0.0.0.0` is not a valid domain for the **Cross-Origin-Opener-Policy**, use `localhost` instead.

- Set `WORKERS`, **maximum 4**, to start **multiple server processes**.

- Disable progress bar when running in production.

> [!TIP]
> Take a look at the [`.env.example`](./.env.example) file.

---

## Run locally with Poetry or Pip

You will need [Python3.12](https://www.python.org/downloads/release/python-31211/) with [Pip](https://pip.pypa.io/en/stable/installation/) and [Venv](https://docs.python.org/3/library/venv.html) installed.

```bash
# Create new Venv
python3.12 -m venv .venv

# Activate Venv
source .venv/bin/activate

# Update Pip
(.venv) pip install --upgrade pip

# Install Wheel and Poetry
(.venv) pip3 install wheel
(.venv) pip3 install poetry

# Install dependencies with Poetry [1]
(.venv) make install

# Install dependencies with Pip [2]
(.venv) pip3 install -r requirements/requirements.txt

# Run the App locally
(.venv) make run
```

## Run with Docker

You will need [Docker](https://www.docker.com/) installed.

```bash
# Run the App in Docker Container
make docker
```

---

### Data Source

All data we handle is retrieved and obtained **"AS IS"** from [Scopus](https://www.scopus.com)®, maintained by [Elsevier B.V.](https://www.elsevier.com/), a database known for its **curated content of peer-reviewed literature**. We declare that there is **no implied endorsement by the rights owners** and also comply that all use is for [non-commercial academic research](https://dev.elsevier.com/academic_research_scopus.html) and is subject to [our Terms](./TERMS_OF_SERVICE.md), as well as the [Elsevier Terms](https://www.elsevier.com/legal/elsevier-website-terms-and-conditions) and [Scopus Policy](https://dev.elsevier.com/academic_research_scopus.html).

> [!CAUTION]
> **You are strictly prohibited from misuse or attempt to misuse data obtained from the Scopus APIs in violation of [Elsevier API Service Agreement](https://dev.elsevier.com/policy/API-service-agreement.pdf).**

---

### API Key <img src="https://img.shields.io/badge/Required-dc3545" alt="Required">

In accordance with the [API Service Agreement](https://dev.elsevier.com/policy/API-service-agreement.pdf) and [Use Policies](https://dev.elsevier.com/policy.html), **Elsevier** will issue you an **API Key** that grants you a limited license to use the [Scopus APIs](https://dev.elsevier.com/sc_apis.html) integrated with this **web API**, so that you can properly authenticate to query the Scopus database.

It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/), clicking on the **I want an API Key** button and registering. If you are part of an **educational institution**, you can try to confirm if your institution is **registered with Elsevier** to [signing in using your organization's or academic email](https://www.scopus.com/signin.uri).

---

### Keywords <img src="https://img.shields.io/badge/Required-dc3545" alt="Required">

Based on the theme or subject of your research, you must select a **minimum of two** (**required**) and a **maximum of four Keywords**, which will be used to **simultaneously search in the abstracts, keywords, and titles**, and find the documents you are searching for that **contain all of them**.

Using the [combined field `TITLE-ABS-KEY`](https://dev.elsevier.com/sc_search_tips.html), we survey data and the **total of documents found in Scopus** for each combination of keywords [concatenated by the Boolean operator `AND`](https://dev.elsevier.com/sc_search_tips.html).

They must be **written in English**, with a **minimum of 2** and a **maximum of 70 characters**. They can contain **letters**, **numbers**, **spaces**, **hyphens**, **underscores**, [**phrases**, **wildcards**, and the **Boolean operators `OR` and `AND NOT`**](https://dev.elsevier.com/sc_search_tips.html).

> [!WARNING]
> Because **`AND NOT`** can [generate unexpected results](https://dev.elsevier.com/sc_search_tips.html), it should be used in the **last field**.

---

### Institutional Network <img src="https://img.shields.io/badge/Required-dc3545" alt="Required">

Please be aware that the **API Key** will only authenticate correctly if you submit it while using your **academic institution's network**, which must be **registered with Elsevier**. This **does not include** <abbr title="Virtual Private Network">VPN</abbr> or proxy access. Therefore, if you are **fully remote** and **off-campus**, some data may **not be returned**.

---

### Quota and Rate Limits <img src="https://img.shields.io/badge/Important-ffc107" alt="Important">

There's a **maximum limit to the number of requests** we can make to [Scopus APIs](https://dev.elsevier.com/sc_apis.html) using your **API Key**. This **request quota resets every seven days**, and you can **check its availability** in the **details panel after completing your survey**. If requests **exceed the quota or throttling rate**, an **error will be returned**. See the [API Key Settings](https://dev.elsevier.com/api_key_settings.html).

These quotas, are **unique to each** <abbr title="Application Programming Interface">**API**</abbr>. According to the [API Key Settings](https://dev.elsevier.com/api_key_settings.html), for the APIs we are using, **Scopus Search** has a **weekly quota of 20,000**, and **Abstract Retrieval** has a **weekly quota of 10,000**.

---

## Examples

| Keywords             | Total gather | Process time | Loss         |
| -------------------- | ------------ | ------------ | ------------ |
| Web API AND Scopus   | 25           | 3.63s        | 0doc / 0.00% |
| Python AND Scopus    | 141          | 19.26s       | 1doc / 0.71% |
| Bibliographic Survey | 1073         | 246.38s      | 7doc / 0.65% |

> [!TIP]
> <a href="./docs/assets/data/example.csv" download="example.csv">Download a sample survey <abbr title="Comma-Separated Values">CSV</abbr> file</a> and take a look.

---

For questions or concerns please contact me at <sir.silvabmauricio@gmail.com>.

[Terms of Service](./TERMS_OF_SERVICE.md)
&nbsp;&#8226;&nbsp;
[Privacy Policy](./PRIVACY_POLICY.md)
&nbsp;&#8226;&nbsp;
[Cookie Policy](./COOKIE_POLICY.md)
&nbsp;&#8226;&nbsp;
[Attributions](./ATTRIBUTIONS.md)

[License](./LICENSE)
&nbsp;&#8226;&nbsp;
[Translations](./TRANSLATIONS.md)
&nbsp;&#8226;&nbsp;
[Latest Release](https://github.com/mauprogramador/scopus-survey-api/releases/latest)
&nbsp;&#8226;&nbsp;
[Changelog](./CHANGELOG.md)
