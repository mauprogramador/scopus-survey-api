# Release Notes

## [:material-github: `v3.0.0`]({{links.releases}}/v3.0.0){:target="\_blank"} <small>:material-calendar-month: 2024-09-30</small>

See the [⟲ CHANGELOG](https://github.com/mauprogramador/scopus-survey-api/tree/master/CHANGELOG.md) to see all the commits.

### 🔨 Builds

- Remove **BeautifulSoup**
- Move and update **Dockerfile**
- Add **dotenv** to use `.env` variables

### ✨ Features

- Handle scopus quota and rate errors
- Update serializers
- Add article page {{abbr.url}} and rate limit
- Update sleep **rate** factor
- Remove `livereload` logs
- Only shows the **QRCode** when the host is open
- Change article page to abstract api, removing web scrapping
- Serialize data from abstract api
- Update scopus configs and urls for abstract api
- Search params as a dto
- Set new start point to `__main__`
- Include `.env` and set container port
- Load `.env` variables to override app **toml** configuration
- Change **fuzzywuzzy** to **thefuzz**
- Add header and query types
- Add usecases, gateway, and middlewares
- Add http retry request
- Add url and template context builders
- Add abstract metaclasses
- Add dtos and serializers
- Add app exceptions
- Add exception json response serializer
- Add progress bar
- Add mobile qrcode
- Add shutdown signal handler
- Add types and regex patterns
- Add exception error messages
- Pagination to get all articles
- Stop multi threads on app interruption
- Add articles scraping progress log
- Make scraping data in multi thread
- Implement debug logs with {{abbr.json}} data
- Disable **uvicorn** access logging
- Set single logger instance to replace singleton
- Update validation **token** generator
- Add application configuration section
- Update templates and context with `pyproject` data
- Load `pyproject` application configuration
- Control logging in file
- Rename and remap folders to clean architecture
- Upgrade logger and implement logging instead of print
- Set date year automatically
- Change license to **MIT**
- Upgrade venv script
- Update favicon

### ♻️ Refactors

- Remove handle quota and set default workers
- Remove web scrapping code
- Update contracts and logger
- Update names with acronyms
- Remove old tests
- Move and update {{abbr.css}} styles
- Move and add images
- Update javascripts, svgs, and templates
- Update context and routes metadata
- Update dependencies and factory
- Update exception handler and {{abbr.http}} exceptions
- Update multiple properties in **toml** from `pyproject`
- Add app, scopus, and fastapi configs
- Build **Scopus api error** attributes in class itself

### 🧪 Tests

- Update multiple tests
- Add abstract {{abbr.api}} tests
- Add framewok, core, and adapters unit tests
- Add framewok, core, and adapters integration tests
- Add tests mocks and helpers
- Remove scraping code parts
- Update mocks and set static data instead using functions
- Remove scraper mock and move code from data to utils
- Add **unit** tests on dependencies

### 📝 Chores

- Update readme information
- Update text, table columns, and context values
- Change **favicon**
- Update responsibility and showned columns
- Update {{abbr.rest}} Client
- Check if `.env` exists before include it
- Only run docs **workflow** when docs files are updated
- Add example of a `.env` config file
- Remove docker docs and update **Dockerfile**
- Rename from `venv` to `setup` and update it
- Add **toml** as app dependency
- Add language and extra data docs dependencies
- Change formatter to **Black**

### 📄 Docs

- Update releases notes to `v3`
- Update **MKDocs** config and metadata
- Update and add more `pt-BR` docs
- Update and add more `en-US` docs
- Add overrides icons and partials {{abbr.html}}
- Add assets data, custom {{abbr.css}}, and all images
- Add `pyproject` configuration
- Fix translation alternate {{abbr.url}} error
- Add fields examples, response body and count field config
- Add notes and remove count field config
- Upgrade article preview page example {{abbr.url}}

### 🎨 Styles

- Update **swagger** route description
- Update docstrings, messages and descriptions
- Rename shell script from venv to setup

## [:material-github: `v2.0.0`]({{links.releases}}/v2.0.0){:target="\_blank"} <small>:material-calendar-month: 2024-03-11</small>

See the [⟲ CHANGELOG](https://github.com/mauprogramador/scopus-survey-api/tree/master/CHANGELOG.md) to see all the commits.

### ✨ Features

- Add table web page, including {{abbr.html}}, {{abbr.css}}, and Javascript
- Add **similarity filter**
- Update {{abbr.http}} helper with request **retry** mechanism
- Add table route, descriptions, and web tag
- Update pyproject metadata and add **FuzzyWuzzy** library

### 🧪 Tests

- Update and add more tests
- Update and add mock data and helpers

### 📄 Docs

- Add {{abbr.csv}} example and images assets
- Update getting started
- Add **similarity filter**
- Add hooks, actions, and new error
- Update links

## [:material-github: `v1.0.0`]({{links.releases}}/v1.0.0){:target="\_blank"} <small>:material-calendar-month: 2024-02-27</small>

See the [⟲ CHANGELOG](https://github.com/mauprogramador/scopus-survey-api/tree/master/CHANGELOG.md) to see all the commits.

## ✨ Features

- Add **GitHub** workflows
- Add static files, including {{abbr.css}}, Javascript, images and icons
- Add web application {{abbr.html}} templates
- Add application middleware, routes/endpoints, and data for swagger
- Add application dependencies to get query params and **Access Token**
- Add gateway for **Scopus Search API**, including {{abbr.http}} helper
- Add logger and lifespan
- Add application core, including models, usecases, and interfaces
- Add {{abbr.http}} exceptions, exception handler, and exception responses

## 🧪 Tests

- Add all application test files
- Add helpers, models, and mock data
- Add {{abbr.rest}} Client file

## 📄 Docs

- Add **Portuguese** (`pt-BR`) documentation
- Add **English** (`en-US`) documentation
- Add Index and static images
- Add **Mkdocs** configuration file

## 📌 Others

- Add all configuration files, including docker and requirements
