# Attributions

**Scopus Survey API** - _Web API for bibliographic survey of Scopus articles_

> _Last updated: August 25, 2025_

Federal Institute of Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Technology in Systems Analysis and Development - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

<br>

## Data Source

All data we handle is retrieved and obtained **"AS IS"** from [Scopus](https://www.scopus.com)®, maintained by [Elsevier B.V.](https://www.elsevier.com/), using the [Scopus APIs](https://dev.elsevier.com/sc_apis.html).

We declare that there is no implied endorsement of Scopus and also comply that all use is for [non-commercial academic research](https://dev.elsevier.com/academic_research_scopus.html) and is subject to our [Terms](./TERMS_OF_SERVICE.md), as well as the [Elsevier Terms](https://www.elsevier.com/legal/elsevier-website-terms-and-conditions) and [Scopus Policy](https://dev.elsevier.com/academic_research_scopus.html).

<br>

## Design

I deliberately chose to base the code and its structure on the [Clean Code](https://blog.cleancoder.com), [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html), and [PEP8](https://peps.python.org/pep-0008/) guidelines.

The web page design was designed and built by me, but I drew inspiration from the following websites:

- [Scopus preview](https://www.scopus.com/standard/marketing.uri)
- [Scopus Search API documentation](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)
- [Scopus Author Search](https://www.scopus.com/freelookup/form/author.uri)
- [Scopus Support Center](https://service.elsevier.com/app/home/supporthub/scopus/)
- [Federal Institute of Mato Grosso do Sul homepage](https://www.ifms.edu.br/)
- [Bootstrap documentation](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)

<br>

## Icons and Images

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

Use does not imply endorsement or affiliation by the owners.

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

[**Ubuntu**](https://design.ubuntu.com/font)

- **Styles:** `Regular 400`, `Medium 500`, `Bold 700`
- **Source:** [Google Fonts](https://fonts.google.com/specimen/Ubuntu)
- **Design:** [Dalton Maag](https://www.daltonmaag.com/)
- **License:** [UBUNTU FONT LICENCE Version 1.0](https://ubuntu.com/legal/font-licence)

<br>

## Technologies

Language

- [Python `v3.11`]({{links.python}})

Development Environment Tools

- [Visual Studio Code `v1.86.1`](https://code.visualstudio.com/)
- [Makefile GNU Make `v4.2.1`](https://www.gnu.org/software/make/manual/make.html)
- [REST Client `v0.25.1` - VsCode Extension](https://github.com/Huachao/vscode-restclient)

Docker

- [Docker `v25.0.3`](https://www.docker.com/)

Framework

- [FastAPI `v0.109.2`](https://fastapi.tiangolo.com/)

Dependency Management

- [Poetry `v1.7.1`](https://python-poetry.org/)

Application Dependencies

- [Pandas `v2.2.0`](https://pandas.pydata.org/docs/index.html)
- [Pydantic `v2.6.1`](https://docs.pydantic.dev/latest/)
- [TheFuzz `v0.22.1`]({{links.pypi}}/fuzzywuzzy/)
- [Python-Levenshtein `v0.25.0`]({{links.pypi}}/python-Levenshtein/)
- [tqdm `v4.66.5`]({{links.pypi}}/tqdm/)

Linting and Formating Dependencies

- [Isort `v5.13.2`](https://pycqa.github.io/isort/)
- [Flake8 `v3.8.3`](https://flake8.pycqa.org/en/latest/)
- [Pylint `v3.0.3`](https://pylint.readthedocs.io/en/stable/)
- [MyPy `v1.8.0`](https://mypy.readthedocs.io/en/stable/)
- [Radon `v6.0.1`](https://radon.readthedocs.io/en/latest/)

Vulnerability and Security Issues Dependencies

- [Bandit `v1.7.7`](https://bandit.readthedocs.io/en/latest/)
- [Pip-Audit `v2.7.0`]({{links.pypi}}/pip-audit/#description)

Test Dependencies

- [Pytest `v8.0.0`](https://docs.pytest.org/en/8.0.x/)
- [Pytest-Mock `v3.12.0`](https://pytest-mock.readthedocs.io/en/latest/)
- [Pytest-Asyncio `v0.23.5`](https://pytest-asyncio.readthedocs.io/en/latest/)
- [Coverage `v7.4.3`](https://coverage.readthedocs.io/en/7.4.3/)

Documentation Dependencies

- [MkDocs `v1.5.3`](https://www.mkdocs.org/)
- [MkDocs-Material `v9.5.9`](https://squidfunk.github.io/mkdocs-material/)
- [MkDocs static i18n plugin `v1.2.3`]({{links.pypi}}/mkdocs-static-i18n/)
- [MKDocs markdown extra data plugin `v0.2.5`]({{links.pypi}}/mkdocs-markdownextradata-plugin/)
