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

**🌐 Idiomas:** Leia em [**`Português [pt-BR]`**](./README.pt_BR.md)<br>

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul &nbsp;&#8226;&nbsp; [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br>
Tecnologia em Análise e Desenvolvimento de Sistemas &nbsp;&#8226;&nbsp; [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br>

> _Federal Institute of Education, Science and Technology of Mato Grosso do Sul_ <br>
> _Technology in Systems Analysis and Development_

Data provided by [Scopus](https://www.scopus.com)® &nbsp;&#8226;&nbsp; © [Elsevier](https://www.elsevier.com)

- Documentation: <https://mauprogramador.github.io/scopus-survey-api/>
- Web API: <http://127.0.0.1:8000/v2/scopus-survey/en-US/survey-bibliographies>
- Swagger UI: <http://127.0.0.1:8000/>

<br>

## 1. Overview

This **web API** is designed to perform **systematic bibliographic surveys using data from the [Scopus database](https://www.elsevier.com/products/scopus)**, promoting access to relevant and high-quality bibliographic sources through a simple and well-documented interface, thus reducing the initial barrier to entry for **students** and academics.

As a [free, non-commercial academic automation tool](https://dev.elsevier.com/academic_research_scopus.html), the application integrates **multiple selection criteria**, including multiple query parameters, keyword combinations, and [Boolean search](https://dev.elsevier.com/sc_search_tips.html), with **mechanisms** for retrieval, validation, serialization, and customized filtering of **large volumes of data** from the [Scopus APIs](https://dev.elsevier.com/sc_apis.html).

This way, only the **most relevant and recent data** will be retained and returned in a **CSV file**, making it suitable bibliometric studies and surveys, research, [systematic reviews](https://en.wikipedia.org/wiki/Systematic_review), etc., allowing students to quickly gather a set of peer-reviewed literature sources for a thesis or project.

<br>

## 2. Configuration

Create an `.env` file to configure the following options:

| **Parameter**  | **Description**                                          | **Default** |
| -------------- | -------------------------------------------------------- | ----------- |
| `SECRET_KEY`   | Used to signed the CSRF Tokens                           |             |
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

- In production, `RELOAD`, `DEBUG`, and `PROGRESS_BAR` are automatically disabled.

> [!TIP]
> Take a look at the [`.env.example`](./.env.example) file.

<br>

## 3. Run

### 3.1. Set Up a Python Venv

You will need [Python3.12](https://www.python.org/downloads/release/python-31211/) with [Pip](https://pip.pypa.io/en/stable/installation/) and [Venv](https://docs.python.org/3/library/venv.html) installed.

```bash
# Create new Venv (.venv)
make venv

# Activate Venv
source .venv/bin/activate
```

### 3.2. Run in Development (Poetry)

Install [Poetry](https://python-poetry.org/) with all dependencies: `app`, `dev`, `tests`, `docs`, and run with [Uvicorn](https://uvicorn.dev/).

```bash
# Install all dependencies groups from pyproject.toml with Poetry
(.venv) make install-dev

# Run with Poetry
(.venv) make run-dev
```

### 3.3. Run in Production (Pip)

Install only the main dependencies: `app` and run with [Gunicorn](https://gunicorn.org/).

```bash
# Install only main dependencies from requirements.txt with Pip
(.venv) make install-prod

# Run with Gunicorn
(.venv) make run-prod
```

### 3.4. Run in Docker

You will need [Docker](https://www.docker.com/) installed. Build the `scopus-survey-api` image from the [Dockerfile](https://docs.docker.com/reference/dockerfile/), install only the main dependencies from `requirements.txt` with [Pip](https://pip.pypa.io/en/stable/installation/), and run with [Uvicorn](https://uvicorn.dev/).

```bash
# Run in Docker Container from Dockerfile
make docker

# Follow and show the last logs
make docker-logs
```

<br>

## 4. Important Information

### 4.1. Data Source

We declare that all use of the [Scopus](https://www.scopus.com)® [database](https://www.elsevier.com/products/scopus) and its [APIs](https://dev.elsevier.com/sc_apis.html), owned and maintained by © [Elsevier B.V.](https://www.elsevier.com/), is intended only for [non-commercial academic research](https://dev.elsevier.com/academic_research_scopus.html), **without implying endorsement or affiliation**, and is subject to [our Terms](./legal/en_US/TERMS_OF_SERVICE.md), as well as [Elsevier's Terms](https://www.elsevier.com/legal/elsevier-website-terms-and-conditions) and [Scopus's Policy](https://dev.elsevier.com/academic_research_scopus.html). All data we handle is retrieved and obtained **"AS IS"** and, therefore, despite its known reliability, we do not guarantee or assume responsibility for any errors or inaccuracies in the data in the Scopus database.

> [!CAUTION]
> **You are strictly prohibited from misuse or attempt to misuse data obtained from the Scopus APIs in violation of [Elsevier API Service Agreement](https://dev.elsevier.com/policy/API-service-agreement.pdf).**

### 4.2. Data Manipulation

In general, the data will be preserved without any direct alteration. However, since they are obtained **"AS IS"**, it will need to be properly validated based on the response fields from the APIs:

- Those that returned a value will be kept as is;
- Those that did not return any value will be set to "`None`" by default;
- The "`authors`" field will be set to the first author ("`dc:creator`") or all authors ("`authors`") concatenated, depending on what is returned.

Finally, the documents will be **filtered and removed** in the following order:

1. Exact duplicates, where the first one will be kept.
2. Exactly the same title and same author(s), where the first one will be kept.
3. Same author(s) with similar titles, where the one with the most recent publication date will be kept.

### 4.3. Search

We use the [combined field "`TITLE-ABS-KEY`"](https://dev.elsevier.com/sc_search_tips.html) to **simultaneously search for keyword combinations in abstracts, keywords, and titles, and retrieve the literature where they are found**. We also use the "`date`" and "`sort`" fields to delimit the period of interest for publications, and sort by year and date of publication and by relevance, alongside other **optional additional** fields in the search to produce more relevant results.

Regarding the survey flow, we first retrieve the total number of results found for each keyword combination, then perform the final survey with the selected combination to obtain the **Scopus ID** of all results, finally retrieving a complete dataset with comprehensive metadata, obtaining all fields with relevant bibliographic information.

### 4.3. API Key

In accordance with the [API Service Agreement](https://dev.elsevier.com/policy/API-service-agreement.pdf) and [Use Policies](https://dev.elsevier.com/policy.html), **Elsevier** will issue you an **API Key** that grants you a limited license to use the [Scopus APIs](https://dev.elsevier.com/sc_apis.html), so that you can properly authenticate to query the Scopus database. It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/) and registering. If you are part of an **educational institution**, you can try to [signing in using your organization's or academic email](https://www.scopus.com/signin.uri).

### 4.4. Institutional Network

Please be aware that the **API Key** will only authenticate correctly if you submit it while using your **academic institution's network**, which must be **registered with Elsevier**. This **does not include** <abbr title="Virtual Private Network">VPN</abbr> or proxy access. Therefore, if you are **fully remote** and **off-campus**, some data may **not be returned**.

### 4.5. Quota and Rate Limits

There's a **maximum limit to the number of requests** we can make to [Scopus APIs](https://dev.elsevier.com/sc_apis.html) using your **API Key**. This **request quota resets every seven days**, is **unique to each API**, and you can **check its availability** in the **details panel after each operation**. If requests **exceed the quota or throttling rate**, an **error will be returned**. See the [API Key Settings](https://dev.elsevier.com/api_key_settings.html).

| Scopus API             | Weekly Quota | Rate Limit |
| ---------------------- | ------------ | ---------- |
| Search API             | 20,000       | 9req/s     |
| Abstract Retrieval API | 10,000       | 9req/s     |

<br>

## 5. Results

### 5.1. Fields Retrieved

Mapped fields of the CSV file

| Field                     | Column                   | Description                                   |
| :------------------------ | :----------------------- | :-------------------------------------------- |
| link `ref=scopus`         | Article Preview Page URL | Scopus article preview page URL               |
| `dc:identifier`           | Scopus ID                | Article Scopus ID                             |
| `authors` or `dc:creator` | Authors                  | Complete author list or only the first author |
| `dc:title`                | Title                    | Article title                                 |
| `prism:publicationName`   | Publication Name         | Source title                                  |
| `dc:description`          | Abstract                 | Article complete abstract                     |
| `prism:coverDate`         | Date                     | Article complete abstract                     |
| `eid`                     | Electronic ID            | Article Electronic ID                         |
| `prism:doi`               | DOI                      | Document Object Identifier                    |
| `prism:volume`            | Volume                   | Identifier for a serial publication           |
| `citedby-count`           | Citations                | Cited-by count                                |

### 5.2. CSV Metadada

Since the result of the survey is a CSV file, which is essentially a dataset obtained from the Scopus APIs, we must [**acknowledge** both Scopus and Elsevier as **data sources**](https://dev.elsevier.com/tecdoc_attribution_scopus.html). Therefore, we will add some metadata at the **top of the file (4 lines) as comments** indicating the parameters used, survey details, and the date the data was obtained.

**Example:**

```txt
# GeneratedBy: ScopusSurveyAPI https://github.com/mauprogramador/scopus-survey-api
# Params: api_key=..., date=2023-2026, keywords=['Python', 'Web API', 'Scopus', 'bibliographic survey'], combination=Web API, ratio=80
# Survey: scopus_total=3126, items_per_page=25, pages_count=126, total_retrieved=3126, total_final=3113, loss=13 (0.42%)
# Source: data retrieved from Scopus APIs on July 23, 2026 via http://api.elsevier.com and http://www.scopus.com.
```

> [!TIP]
> <a href="./docs/assets/data/example.csv" download="example.csv">Download a sample survey <abbr title="Comma-Separated Values">CSV</abbr> file</a> and take a look.

### 5.3. Performance (v3.2.6)

| Total gather | Process time    | Loss      | Throughput   | Latency      |
| ------------ | --------------- | --------- | ------------ | ------------ |
| 8            | 2.36s           | 0 (0.00%) | 0.295 s/item | 3.39 items/s |
| 36           | 5.92s           | 0 (0.00%) | 0.164 s/item | 6.08 items/s |
| 106          | 18.70s          | 1 (0.93%) | 0.174 s/item | 5,72 items/s |
| 284          | 38.47s          | 2 (0.70%) | 0.134 s/item | 7.43 items/s |
| 307          | 42.92s          | 2 (0.65%) | 0.139 s/item | 7.15 items/s |
| 966          | 128.06s (2.13m) | 0 (0.00%) | 0.133 s/item | 7.54 items/s |
| 3,126        | 412.03s (6.86m) | 0 (0.00%) | 0.132 s/item | 7.59 items/s |

Overall performance improved **significantly at scale** compare to the last release, yielding a **~1.75x speedup (73% increase in throughput)** and a **~42-45% reduction in processing time per item** for large batches.

More importantly, the new implementation **eliminated scaling degradation**, so the throughput remains flat and stable at **~7.5 to 7.6 items/sec**, even when scaling up to **3,126 items**.

Throughput at scale increased from **4.36 items/sec to ~7.59 items/sec** (a **+74.1% increase** in work done per second). It takes **~42% less time** to process the same dataset size now.

<br>

## Citation

If scopus-survey-pi helped you getting data for research, please cite it:

📝 **APA**

```text
Batista, M. d. S. (2025). Scopus Survey API: Web API for bibliographic survey of Scopus articles (Version 3.2.6) [Web API]. GitHub. https://github.com/mauprogramador/scopus-survey-api.
```

📝 **ABNT** &nbsp; `pt-BR`

```text
BATISTA, Maurício da Silva. Scopus Survey API: API da Web para levantamento bibliográfico de artigos da Scopus. Versão 3.2.6. [Web API]. GitHub, 2025. Disponível em: https://github.com/mauprogramador/scopus-survey-api. Acesso em: DD MMM. YYYY.
```

<br>

---

For questions or concerns please contact me at <sir.silvabmauricio@gmail.com>.

[Terms of Service](./legal/en_US/TERMS_OF_SERVICE.md)
&nbsp;&#8226;&nbsp;
[Privacy Policy](./legal/en_US/PRIVACY_POLICY.md)
&nbsp;&#8226;&nbsp;
[Cookie Policy](./legal/en_US/COOKIE_POLICY.md)
&nbsp;&#8226;&nbsp;
[Attributions](./legal/en_US/ATTRIBUTIONS.md)

[License](./LICENSE)
&nbsp;&#8226;&nbsp;
[Translations](./TRANSLATIONS.md)
&nbsp;&#8226;&nbsp;
[Latest Release](https://github.com/mauprogramador/scopus-survey-api/releases/latest)
&nbsp;&#8226;&nbsp;
[Changelog](./CHANGELOG.md)
