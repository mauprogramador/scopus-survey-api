# Attributions

**Scopus Survey API** - _Web API for bibliographic survey of Scopus articles_

> _Last updated: May 13, 2026_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br>

> _Federal Institute of Education, Science and Technology of Mato Grosso do Sul_ <br>
> _Technology in Systems Analysis and Development_

<br>

## Notice

This project incorporates various resources, including fonts, images, icons, logos, and design elements. All external resources used in this project are properly licensed and used according to their respective terms of use.

<br>

## Data Source

All data we handle is retrieved and obtained **"AS IS"** from [Scopus](https://www.scopus.com)®, maintained by © [Elsevier B.V.](https://www.elsevier.com/), using the [Scopus APIs](https://dev.elsevier.com/sc_apis.html).

We declare that there is no implied endorsement of Scopus and also comply that all use is for [non-commercial academic research](https://dev.elsevier.com/academic_research_scopus.html) and is subject to our [Terms](./TERMS_OF_SERVICE.md), as well as the [Elsevier Terms](https://www.elsevier.com/legal/elsevier-website-terms-and-conditions) and [Scopus Policy](https://dev.elsevier.com/academic_research_scopus.html).

<br>

## Code

This project adopts industry-standard software development practices to ensure maintainability, scalability, and collaboration. We implement:

- [PEP8](https://peps.python.org/pep-0008/) Guidelines: following the official Python style guide for consistent and readable code, aligned with community standards.

- [Clean Code](https://blog.cleancoder.com) Principles: writing self-documenting code that emphasizes clarity, simplicity, and intentionality in every implementation.

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html): structuring our system with separation of concerns, independent frameworks, and testable business logic at its core.

<br>

## Web Design

The web page design draws inspiration from various public domain sources and freely available resources. While certain design elements, color schemes, typographic choices, or layout concepts may resemble other works, all implementation code was developed independently and built by me [@mauprogramador](https://github.com/mauprogramador).

I took inspiration from the following websites:

- [Scopus preview](https://www.scopus.com/standard/marketing.uri)
- [Scopus Search API documentation](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)
- [Scopus Author Search](https://www.scopus.com/freelookup/form/author.uri)
- [Scopus Support Center](https://service.elsevier.com/app/home/supporthub/scopus/)
- [Instituto Federal de Mato Grosso do Sul homepage](https://www.ifms.edu.br/)
- [Bootstrap documentation](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)

<br>

## Icons

The icons we use are from freely available or openly licensed (with proper attribution) icon repositories.

[**Material Symbols and Icons**](https://fonts.google.com/icons)

- **License:** Apache License Version 2.0.

[**Bootstrap Icons**](https://icons.getbootstrap.com/)

- **License:** MIT License

[**SVG Repo**](https://www.svgrepo.com/)

- `Page Separator SVG Vector`
  - **Creator:** [Remix Design](https://www.svgrepo.com/author/Remix%20Design/)
  - **License:** Apache License

- `Lock Open Alt SVG Vector`
  - **Creator:** [Iconscout](https://www.svgrepo.com/author/Iconscout/)
  - **License:** Apache License

<br>

## Logos

The logos we use are from permitted brand guidelines or sourced from public domain websites. Their use does not imply endorsement or affiliation by the owners.

- **Scopus (Shortcut Icon):**
  - **File:** `scopus.ico`
  - **Owner:** © Elsevier B.V.
  - **Source:** [Scopus preview](https://www.scopus.com/) (shortcut icon)
  - **Use:** footer reference to the data source website

- **IFMS (Shortcut Icon)**
  - **File:** `ifms.ico`
  - **Owner:** © 2009-2022 Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul
  - **Source:** [Página Inicial - IFMS](https://www.ifms.edu.br/) (shortcut icon)
  - **Use:** footer reference to the institution website

- **DEV**
  - **File:** `dev.png`
  - **Owner:** DEV Community © 2016 - 2025
  - **Source:** [DEV Brand Guidelines](https://dev.to/brand)
  - **Use:** footer reference to the author's profile

<br>

## Fonts

The font used in this project is properly licensed and free for commercial use.

[**Ubuntu**](https://design.ubuntu.com/font)

- **Styles:** `Regular 400`, `Medium 500`, `Bold 700`
- **Source:** [Google Fonts](https://fonts.google.com/specimen/Ubuntu)
- **Design:** [Dalton Maag](https://www.daltonmaag.com/)
- **License:** [UBUNTU FONT LICENCE Version 1.0](https://ubuntu.com/legal/font-licence)

<br>

## Technologies

Language

- [Python `v3.12.11`](https://www.python.org/downloads/release/python-3120/)

Development Environment Tools

- [Visual Studio Code `v1.104.0`](https://code.visualstudio.com/)
- [Makefile GNU Make `v4.3.0`](https://www.gnu.org/software/make/manual/make.html)
- [REST Client `v0.25.1` - VsCode Extension](https://github.com/Huachao/vscode-restclient)

Docker

- [Docker `v28.4.0`](https://www.docker.com/)

Framework

- [FastAPI `v0.115.14`](https://fastapi.tiangolo.com/)

Dependency Management

- [Poetry `v2.1.3`](https://python-poetry.org/)

Application Dependencies

- [Pandas `v2.3.1`](https://pandas.pydata.org/docs/index.html)
- [Pydantic `v2.11.7`](https://docs.pydantic.dev/latest/)
- [Pydantic-Settings `v2.11.7`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Itsdangerous `v2.2.0`](https://itsdangerous.palletsprojects.com/en/stable/)
- [SlowAPI `v0.1.9`](https://slowapi.readthedocs.io/en/latest/)
- [AIOHTTP `v3.12.15`](https://docs.aiohttp.org/en/stable/)
- [AIOHTTP-Retry `v2.9.1`](https://github.com/inyutin/aiohttp_retry)
- [AIOLimiter `v1.2.1`](https://aiolimiter.readthedocs.io/en/stable/)
- [Uvloop `v0.21.0`](https://uvloop.readthedocs.io/)
- [Gunicorn `v23.0.0`](https://gunicorn.org/)
- [Uvicorn-worker `v0.4.0`](https://github.com/Kludex/uvicorn-worker)
- [TheFuzz `v0.22.1`](https://github.com/seatgeek/thefuzz)
- [Python-Levenshtein `v0.27.1`](https://pypi.org/project/python-Levenshtein/)
- [tqdm `v4.67.5`](https://pypi.org/project/tqdm)

Application Sub-Dependencies

- [Uvicorn `v0.38.0`](https://uvicorn.dev/) - FastAPI
- [Jinja2 `v3.1.6`](https://jinja.palletsprojects.com/en/stable/) - FastAPI
- [Starlette `v0.46.2`](https://www.starlette.dev/) - FastAPI

Application Built-in Dependencies

- [Asyncio `py v3.12`](https://docs.python.org/3.12/library/asyncio.html)
- [Concurrent.futures `py v3.12`](https://docs.python.org/3.12/library/concurrent.futures.html)
- [Urllib `py v3.12`](https://docs.python.org/3.12/library/urllib.html)
- [Typing `py v3.12`](https://docs.python.org/3.12/library/typing.html)
- [Gettext `py v3.12`](https://docs.python.org/3.12/library/gettext.html)
- [Itertools `py v3.12`](https://docs.python.org/3.12/library/itertools.html)
- [Logging `py v3.12`](https://docs.python.org/3.12/library/logging.html)

Web Dependencies

- [Bootstrap `v5.3.7`](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [JSON View `v1.0.0`](https://github.com/pgrabovets/json-view)

Linting and Formating Dependencies

- [Isort `v6.0.1`](https://pycqa.github.io/isort/)
- [Pylint `v3.3.7`](https://pylint.readthedocs.io/en/stable/)
- [MyPy `v1.17.1`](https://mypy.readthedocs.io/en/stable/)
- [Black `v25.1.0`](https://black.readthedocs.io/en/stable/)
- [Radon `v6.0.1`](https://pypi.org/project/radon/)

Vulnerability and Security Dependencies

- [Bandit `v1.8.6`](https://pypi.org/project/bandit/)
- [Pip-Audit `v2.9.0`](https://pypi.org/project/pip-audit)

Test Dependencies

- [Pytest `v8.4.1`](https://docs.pytest.org/en/8.0.x/)
- [Pytest-Mock `v3.14.1`](https://pytest-mock.readthedocs.io/en/latest/)
- [Pytest-Asyncio `v1.1.0`](https://pytest-asyncio.readthedocs.io/en/latest/)
- [Coverage `v7.10.2`](https://coverage.readthedocs.io/en/7.4.3/)

Documentation Dependencies

- [MkDocs `v1.6.1`](https://www.mkdocs.org/)
- [MkDocs-Material `v9.6.16`](https://squidfunk.github.io/mkdocs-material/)
- [MkDocs Static I18n Plugin `v1.3.0`](https://pypi.org/project/mkdocs-static-i18n/)
- [MKDocs Markdown Extra Data Plugin `v0.2.6`](https://pypi.org/project/mkdocs-markdownextradata-plugin/)
