# Reference

Here is the **Web** {{abbr.api}} code or reference, providing details about the classes, methods, parameters, attributes, and each part of this application.

```text
.
├── app
│   ├── adapters/
│   |   ├── factories/
│   |   ├── gateway/
│   |   ├── helpers/
|   |   └── presenters/
│   ├── core/
│   |   ├── common/
│   |   ├── config/
│   |   ├── data/
│   |   ├── domain/
|   |   └── usecases/
│   ├── framework/
│   |   ├── dependencies/
│   |   ├── exceptions/
│   |   ├── fastapi/
│   |   └── middleware/
│   └── utils/
```

<br>
<!-- SearchParams -->

## <code class="badge-class"></code> <span class="code-class">SearchParams</span>

:material-text-box: Type validator for **API Key** and **Keywords** search params<br>
:material-github: [`source code`]({{links.common}}/types.py){:target="\_blank"}
:material-package-variant-closed: `core.common`<br>
:material-file-code: `app/core/common/types.py`<br>

```py
class SearchParams(
    api_key: str = Field(),
    keywords: Keywords = Field()
)
```

A model **validator** built using [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} for the **API Key** and **Keywords** parameters used in the **Scopus Search API** search, validating their typing and values using the [Pydantic `Field()`]({{links.field}}){:target="\_blank"} function.

!!! note

    Read more about the **API Key** and **Keywords** rules and specifications in the [requirements section](./requirements.md).

| **Parameter** | **Type**   | **Description**               |
| ------------- | ---------- | ----------------------------- |
| `api_key`     | `str`      | **API Key** search parameter  |
| `keywords`    | `Keywords` | **Keywords** search parameter |

<br>
<!-- ScopusResult -->

## <code class="badge-class"></code> <span class="code-class">ScopusResult</span>

:material-text-box: Serializer for entry field item in response {{abbr.json}} schema<br>
:material-github: [`source code`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusResult(
    link: str = Field(),
    url: str = Field()
    scopus_id: str = Field()
)
```

A model **serializer** built using [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} for the entry items in the **Scopus Search API** search response, parsing them in code using the [Pydantic `Field()`]({{links.field}}){:target="\_blank"} function.

| **Parameter** | **Type** | {{abbr.json}} **Field** | **Description**                                 |
| ------------- | -------- | ----------------------- | ----------------------------------------------- |
| `link`        | `str`    | `@_fa`                  | Top-level navigation links                      |
| `url`         | `str`    | `prism:url`             | **Content Abstract Retrieval API** {{abbr.uri}} |
| `scopus_id`   | `str`    | `dc:identifier`         | Article **Scopus ID**                           |

<br>
<!-- ScopusSearch -->

## <code class="badge-class"></code> <span class="code-class">ScopusSearch</span>

:material-text-box: Serializer for **Scopus Search API** response {{abbr.json}} schema<br>
:material-github: [`source code`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusSearch(
    total_results: int = Field(),
    items_per_page: int = Field(),
    entry: list[ScopusResult] = Field()
)
```

A model **serializer** built using the [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} for the **Scopus Search API** {{abbr.json}} response, parsing it in code using the [Pydantic `Field()`]({{links.field}}){:target="\_blank"} function.

Before **validation**, it will access the `search-results` {{abbr.json}} field to flatten the hierarchy and get the actual data.

!!! info

    Flattening is the process of transforming a nested {{abbr.json}} data structure into a single level of key-value pairs.

| **Parameter**    | **Type**             | {{abbr.json}} **Field**   | **Description**                                               |
| ---------------- | -------------------- | ------------------------- | ------------------------------------------------------------- |
| `total_results`  | `int`                | `opensearch:totalResults` | Total number of articles found                                |
| `items_per_page` | `int`                | `opensearch:itemsPerPage` | Number of articles divided into each page                     |
| `entry`          | `list[ScopusResult]` | `entry`                   | Lists of article data with the fields specified in the search |

!!! note

    Read more about the returned [{{abbr.json}} body and its fields](./scopus-search-api.md/#response-body).

### <code class="badge-property"></code> <span class="code-property">pages_count</span>

```py
def pages_count() -> int
```

Calculates the **number of pages** by dividing the **total results** by the number of **items per page**, returning the **smallest `int`** using the [math `ceil()`]({{links.pythonDocs}}/math.html#math.ceil){:target="\_blank"} function.

<br>
<!-- ScopusQuotaRateLimit -->

## <code class="badge-class"></code> <span class="code-class">ScopusQuotaRateLimit</span>

:material-text-box: Serializer for **Scopus APIs** responses<br>
:material-github: [`source code`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusQuotaRateLimit(
    reset: float = Field(),
    status: str = Field(),
    error_code: str = Field()
)
```

A model **serializer** built using [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} for the **Scopus APIs** responses, parsing them in code using the [Pydantic `Field()`]({{links.field}}){:target="\_blank"} function.

Before **validation**, it will retrieve the response headers and get the `error-response` response {{abbr.json}} field if present.

| **Parameter** | **Type** | **Response Field**  | **Description**                                               |
| ------------- | -------- | ------------------- | ------------------------------------------------------------- |
| `reset`       | `float`  | `X-RateLimit-Reset` | Date/Time in **Epoch** seconds when {{abbr.api}} quota resets |
| `status`      | `str`    | `X-ELS-Status`      | Elsevier server/**Scopus** {{abbr.api}} status                |
| `error_code`  | `str`    | `error-code`        | Elsevier server/**Scopus** {{abbr.api}} error code            |

!!! info

    [Epoch](https://en.wikipedia.org/wiki/Epoch_(computing)){:target="\_blank"} is the number of seconds that have elapsed since January 1, 1970, also known as [Unix time](https://en.wikipedia.org/wiki/Unix_time){:target="\_blank"}.

### <code class="badge-property"></code> <span class="code-property">reset_datetime</span>

```py
def reset_datetime() -> str
```

Convert the **epoch timestamp** from the **quota reset header** to a `datetime`, format it, and return it as a more understandable `str` of the datetime, telling when the {{abbr.api}} **request quota** will be reset.

### <code class="badge-property"></code> <span class="code-property">quota_exceeded</span>

```py
def quota_exceeded() -> bool
```

Check the value of the response **status header**, returning `True` if it is equal to `QUOTA_EXCEEDED - Quota Exceeded` and `False` otherwise.

!!! note

    Learn more about the [{{abbr.api}} request quota limit]({{links.scApiKey}}){:target="\_blank"}.

### <code class="badge-property"></code> <span class="code-property">rate_limit_exceeded</span>

```py
def rate_limit_exceeded() -> bool
```

Check the value of the response **error code field**, returning `True` if it is equal to `RATE_LIMIT_EXCEEDED` and `False` otherwise.

!!! note

    Learn more about the [{{abbr.api}} request throttling rate limit]({{links.scApiKey}}){:target="\_blank"}.

<br>
<!-- ScopusAbstract -->

## <code class="badge-class"></code> <span class="code-class">ScopusAbstract</span>

:material-text-box: Serializer for **Scopus Abstract Retrieval API** response {{abbr.json}} schema<br>
:material-github: [`source code`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusAbstract(
    url: str = Field(),
    scopus_id: str = Field(),
    authors: str = Field(),
    title: str = Field(),
    publication_name: str = Field(),
    abstract: str = Field(),
    date: str = Field(),
    eid: str = Field(),
    doi: str = Field(),
    volume: str = Field(),
    citations: str = Field()
)
```

A model **serializer** built using the [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} for the **Scopus abstracts** of the articles in the {{abbr.json}} response, parsing them in code using the [Pydantic `Field()`]({{links.field}}){:target="\_blank"} function and setting to `null` any fields that are not returned.

Before **validation**, the hierarchy will be flattened to get the actual data. First, the `abstracts-retrieval-response` {{abbr.json}} field will be accessed, then the `authors` field will be set from the `author` {{abbr.json}} field, taken from the `authors` {{abbr.json}} field if returned or from the `dc:creator` {{abbr.json}} field otherwise.

!!! info

    Flattening is the process of transforming a nested {{abbr.json}} data structure into a single level of key-value pairs.

Additionally, the **author names** will be selected from the `ce:indexed-name` {{abbr.json}} field in the author data, to be concatenated and returned. Finally, the `coredata` {{abbr.json}} field will be accessed and updated with the author data before returning it.

When deserialized into `dict`, the `date` field, when not `null`, will be formatted as `DD-MM-YYYY`.

| **Parameter**      | **Type** | {{abbr.json}} **Field**   | **Description**                               |
| ------------------ | -------- | ------------------------- | --------------------------------------------- |
| `url`              | `str`    | `link ref=scopus`         | Scopus article preview page URL               |
| `scopus_id`        | `str`    | `dc:identifier`           | Article Scopus ID                             |
| `authors`          | `str`    | `authors` or `dc:creator` | Complete author list or only the first author |
| `title`            | `str`    | `dc:title`                | Article title                                 |
| `publication_name` | `str`    | `prism:publicationName`   | Source title                                  |
| `abstract`         | `str`    | `dc:description`          | Article complete abstract                     |
| `date`             | `str`    | `prism:coverDate`         | Publication date                              |
| `eid`              | `str`    | `eid`                     | Article Electronic ID                         |
| `doi`              | `str`    | `prism:doi`               | Document Object Identifier                    |
| `volume`           | `str`    | `prism:volume`            | Identifier for a serial publication           |
| `citations`        | `str`    | `citedby-count`           | Cited-by count                                |

!!! note

    Read more about the returned fields in the [Scopus Search Views documentation](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"}.

<br>
<!-- AccessToken -->

## <code class="badge-class"></code> <span class="code-class">AccessToken</span>

:material-text-box: Get and validate the **Access** {{abbr.token}}<br>
:material-github: [`source code`]({{links.dependencies}}/access_token.py){:target="\_blank"}
:material-package-variant-closed: `framework.dependencies`<br>
:material-file-code: `app/framework/dependencies/access_token.py`<br>

```py
class AccessToken()(
    request: Request,
    access_token: Annotated[str | None, TokenHeader] = None
)
```

A route [dependency]({{links.fastapiTutorial}}/dependencies/){:target="\_blank"} that implements the `__call__` method to create a [callable instance](https://realpython.com/python-callable-instances/){:target="\_blank"} that will obtain and validate the **Access** {{abbr.token}} header via the [FastAPI `Header()`]({{links.fastapiTutorial}}/header-params/){:target="\_blank"} function or the request.

To provide a little more security, the application will **automatically generate** a {{abbr.token}} that will be passed to the application's {{abbr.api}} web page, which in turn will send it in the **request header** for **validation**.

| **Parameter**  | **Type**        | **Description**                                                                                      |
| -------------- | --------------- | ---------------------------------------------------------------------------------------------------- |
| `request`      | `Request`       | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |
| `access_token` | `str` or `None` | Request {{abbr.token}} header descriptor and validator. **Default:** `None`                          |

<br>
<!-- QueryParams -->

## <code class="badge-class"></code> <span class="code-class">QueryParams</span>

:material-text-box: Get and validate the {{abbr.queryParams}}**s**<br>
:material-github: [`source code`]({{links.dependencies}}/query_params.py){:target="\_blank"}
:material-package-variant-closed: `framework.dependencies`<br>
:material-file-code: `app/framework/dependencies/query_params.py`<br>

```py
class QueryParams()(
    request: Request,
    api_key: Annotated[str | None, APIKeyQuery] = None,
    keywords: Annotated[Keywords | None, KeywordsQuery] = None
)
```

A route [dependency]({{links.fastapiTutorial}}/dependencies/){:target="\_blank"} that implements the `__call__` method to create a [callable instance](https://realpython.com/python-callable-instances/){:target="\_blank"} that will obtain and validate the **API Key** and **Keywords** query parameters via the [FastAPI `Query()`]({{links.fastapiTutorial}}/query-params-str-validations/){:target="\_blank"} function or the request.

| **Parameter** | **Type**             | **Description**                                                                                      |
| ------------- | -------------------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | `Request`            | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |
| `api_key`     | `str` or `None`      | Request **API Key** {{abbr.queryParams}} descriptor and validator. **Default:** `None`               |
| `keywords`    | `Keywords` or `None` | Request **Keywords** {{abbr.queryParams}} descriptor and validator. **Default:** `None`              |

### <code class="badge-method"></code> <span class="code-method">equals</span>

```py
def equals(api_key: str, keywords: list[str]) -> bool
```

Compares the instance's **API Key** and **Keywords** with another **API Key** and **Keywords**, returns `True` if they are equal and `False` otherwise.

| **Parameter** | **Type**    | **Description**            |
| ------------- | ----------- | -------------------------- |
| `api_key`     | `str`       | **API Key** to comparison  |
| `keywords`    | `list[str]` | **Keywords** to comparison |

### <code class="badge-method"></code> <span class="code-method">to_dict</span>

```py
def to_dict() -> dict[str, str | Keywords]
```

Serializes the **API Key** and **Keywords** instance attributes as a `dict`.

<br>
<!-- HTTPRetryHelper -->

## <code class="badge-class"></code> <span class="code-class">HTTPRetryHelper</span>

:material-text-box: Make {{abbr.http}} requests with {{abbr.throttling}} and {{abbr.retry}} mechanisms<br>
:material-github: [`source code`]({{links.helpers}}/http_retry_helper.py){:target="\_blank"}
:material-package-variant-closed: `adapters.helpers`<br>
:material-file-code: `app/adapters/helpers/http_retry_helper.py`<br>

```py
class HTTPRetryHelper(
    for_search: bool = None
)
```

An {{abbr.http}} [client](<https://en.wikipedia.org/wiki/Client_(computing)>){:target="\_blank"} for making requests with the following mechanisms:

- [Throttling](https://www.tibco.com/glossary/what-is-api-throttling){:target="\_blank"}: control the rate of data flow into a service by limiting the number of {{abbr.api}} requests a user can make in a certain period.
- [Retry](https://medium.com/@API4AI/best-practice-implementing-retry-logic-in-http-api-clients-0b5469c08ced){:target="\_blank"}: automatically retry failed operations to recover from unexpected failures and continue functioning correctly.
- [Rate Limiting](https://www.enjoyalgorithms.com/blog/throttling-and-rate-limiting){:target="\_blank"}: limits network traffic by controlling the number of requests that can be made within a given period of time.
- [Session]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"}: persist certain parameters and reuse the same connection across all requests.
- [Cache](<https://en.wikipedia.org/wiki/Cache_(computing)>){:target="\_blank"}: temporarily stores data so that future requests for that data can be fulfilled more quickly.

| **Parameter** | **Type** | **Description**                                                                                                            |
| ------------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| `for_search`  | `bool`   | Indicates in the log message whether the request will be directed to the **Scopus Search API** or not. **Default:** `None` |

### <code class="badge-method"></code> <span class="code-method">mount_session</span>

```py
def mount_session(headers: Headers) -> None
```

Initializes the [session]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"} and mounts it by registering the [cache-control]({{links.pypi}}/CacheControl/){:target="\_blank"} connection adapter with the [retry](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry){:target="\_blank"} configuration.

| **Parameter** | **Type**  | **Description**                                  |
| ------------- | --------- | ------------------------------------------------ |
| `headers`     | `Headers` | The {{abbr.http}} headers to send in the request |

### <code class="badge-method"></code> <span class="code-method">close</span>

```py
def close() -> None
```

Closes the [cache-control]({{links.pypi}}/CacheControl/){:target="\_blank"} connection adapter and [session]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"}.

### <code class="badge-method"></code> <span class="code-method">request</span>

```py
def request(url: str) -> Response
```

Initialize, [prepare with session]({{links.requestsDocs}}/user/advanced/#prepared-requests){:target="\_blank"}, send the request, and then returns the response as a [Requests `Response`]({{links.requestsDocs}}/api/#requests.Response){:target="\_blank"} object.

| **Parameter** | **Type** | **Description**                         |
| ------------- | -------- | --------------------------------------- |
| `url`         | `str`    | The {{abbr.url}} to send the request to |

<br>
<!-- URLBuilderHelper -->

## <code class="badge-class"></code> <span class="code-class">URLBuilderHelper</span>

:material-text-box: Generate and format {{abbr.url}}s for {{abbr.http}} requests<br>
:material-github: [`source code`]({{links.helpers}}/url_builder_helper.py){:target="\_blank"}
:material-package-variant-closed: `adapters.helpers`<br>
:material-file-code: `app/adapters/helpers/url_builder_helper.py`<br>

```py
class URLBuilderHelper()
```

A builder to generate **Scopus API**s resource {{abbr.url}}s and [pagination](https://en.wikipedia.org/wiki/Pagination){:target="\_blank"} {{abbr.url}}.

### <code class="badge-method"></code> <span class="code-method">get_search_url</span>

```py
def get_search_url(keywords: Keywords) -> str
```

Generates **Scopus Search API** resource {{abbr.url}} and returns it as a `str`.

| **Parameter** | **Type**   | **Description**                              |
| ------------- | ---------- | -------------------------------------------- |
| `keywords`    | `Keywords` | The keywords that will be used in the search |

### <code class="badge-method"></code> <span class="code-method">get_pagination_url</span>

```py
def get_pagination_url(page: int) -> str
```

Generates **Scopus Search API** pagination {{abbr.url}} and returns it as a `str`.

| **Parameter** | **Type** | **Description**                            |
| ------------- | -------- | ------------------------------------------ |
| `page`        | `int`    | The page index for the start of pagination |

### <code class="badge-method"></code> <span class="code-method">get_article_page_url</span>

```py
def get_abstract_url(url: str) -> str
```

Generates **Scopus Abstract Retrieval API** resource {{abbr.url}} and returns it as a `str`.

| **Parameter** | **Type** | **Description**                                                  |
| ------------- | -------- | ---------------------------------------------------------------- |
| `url`         | `str`    | The **Scopus Abstract Retrieval API** base resource {{abbr.url}} |

<br>
<!-- ScopusSearchAPI -->

## <code class="badge-class"></code> <span class="code-class">ScopusSearchAPI</span>

:material-text-box: Search and retrieve articles via the **Scopus Search API**<br>
:material-github: [`source code`]({{links.gateway}}/scopus_search_api.py){:target="\_blank"}
:material-package-variant-closed: `adapters.gateway`<br>
:material-file-code: `app/adapters/gateway/scopus_search_api.py`<br>

```py
class ScopusSearchAPI(
    http_helper: HttpRetry,
    url_builder: UrlBuilder
)
```

First, the request headers for the **Scopus API** will be built with the `API Key`, the [resource {{abbr.url}}](./scopus-search-api.md/#api-resource-url) is built with the `API Key` and `Keywords` as search parameters, and then the articles will be searched via the **Scopus Search API**. Then, the response is validated, retrieving the articles if successful, or handling errors otherwise.

An **error** will be returned when: [no articles are found](./responses-and-errors.md/#404-not-found), the `API Key` [quota is exceeded](./api-limit-and-fields-and-filter.md/#quota-exceeded), the **Scopus Search API** returns a [{{abbr.http}} status error](./responses-and-errors.md/#scopus-apis-status-error), and when the [{{abbr.json}} response](./scopus-search-api.md/#response-body) cannot be validated.

!!! note

    Read more about the [quota of how much data an **API Key** can retrieve]({{links.scApiKey}}){:target="\_blank"}.

The articles data will be validated, defaulting to `null` for fields that are not returned. It may use [threads](https://realpython.com/intro-to-python-threading/#what-is-a-thread){:target="\_blank"} with the [ThreadPoolExecutor]({{links.pythonDocs}}/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor){:target="\_blank"} and build the {{abbr.url}} with the **page index** when there are multiple articles to fetch with [pagination](https://en.wikipedia.org/wiki/Pagination){:target="\_blank"}.

| **Parameter** | **Type**     | **Description**                                                            |
| ------------- | ------------ | -------------------------------------------------------------------------- |
| `http_helper` | `HttpRetry`  | Injects [`HttpRetryHelper`](#httpretryhelper) to make the requests         |
| `url_builder` | `UrlBuilder` | Injects [`UrlBuilderHelper`](#urlbuilderhelper) to build the {{abbr.url}}s |

### <code class="badge-method"></code> <span class="code-method">search_articles</span>

```py
def search_articles(search_params: SearchParams) -> list[ScopusResult]
```

Searches for articles via **Scopus Search API**, compiles and returns all retrieved data in a `list` of [`ScopusResult`](#scopusresult){:target="\_blank"}.

| **Parameter**   | **Type**       | **Description**                                          |
| --------------- | -------------- | -------------------------------------------------------- |
| `search_params` | `SearchParams` | Validated **API Key** and **Keywords** search parameters |

<br>
<!-- ScopusAbstractRetrievalAPI -->

## <code class="badge-class"></code> <span class="code-class">ScopusAbstractRetrievalAPI</span>

:material-text-box: Retrieves **Scopus abstracts** via the **Scopus Abstract Retrieval API**<br>
:material-github: [`source code`]({{links.gateway}}/scopus_abstract_retrieval_api.py){:target="\_blank"}
:material-package-variant-closed: `adapters.gateway`<br>
:material-file-code: `app/adapters/gateway/scopus_abstract_retrieval_api.py`<br>

```py
class ScopusAbstractRetrievalAPI(
    http_helper: HttpRetry,
    url_builder: UrlBuilder
)
```

First, the request headers to the **Scopus API** will be built with the `API Key`, the [resource {{abbr.url}}](./scopus-abstract-retrieval-api.md/#final-url) is built from the base [resource {{abbr.url}}](./scopus-abstract-retrieval-api.md/#api-resource-url), and then the **Scopus abstracts** will be retrieved via the **Scopus Abstracts Retrieval API**. The response is then validated, retrieving the abstracts if successful or handling errors otherwise.

An **error** will be returned when: the `API Key` [quota is exceeded](./api-limit-and-fields-and-filter.md/#quota-exceeded), the **Scopus Abstract Retrieval API** returns an [{{abbr.http}} status error](./responses-and-errors.md/#scopus-apis-status-error), and when the [{{abbr.json}} response](./scopus-abstract-retrieval-api.md/#response-body) cannot be validated.

The abstracts data will be validated, defaulting to `null` for fields that are not returned. It can use [threads](https://realpython.com/intro-to-python-threading/#what-is-a-thread){:target="\_blank"} with the [ThreadPoolExecutor]({{links.pythonDocs}}/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor){:target="\_blank"} when there are multiple abstracts to retrieve.

| **Parameter** | **Type**     | **Description**                                                            |
| ------------- | ------------ | -------------------------------------------------------------------------- |
| `http_helper` | `HttpRetry`  | Injects [`HttpRetryHelper`](#httpretryhelper) to make the requests         |
| `url_builder` | `UrlBuilder` | Injects [`UrlBuilderHelper`](#urlbuilderhelper) to build the {{abbr.url}}s |

### <code class="badge-method"></code> <span class="code-method">retrieve_abstracts</span>

```py
def retrieve_abstracts(api_key: str, entry: list[ScopusResult]) -> DataFrame
```

Retrieves **Scopus abstracts** via the **Scopus Abstract Retrieval API**, compiles and returns all fetched data into a [Pandas `DataFrame`]({{links.dataframe}}){:target="\_blank"}.

| **Parameter** | **Type**             | **Description**                      |
| ------------- | -------------------- | ------------------------------------ |
| `api_key`     | `str`                | Validated `API Key` search parameter |
| `entry`       | `list[ScopusResult]` | List of articles data                |

<br>
<!-- ArticlesSimilarityFilter -->

## <code class="badge-class"></code> <span class="code-class">ArticlesSimilarityFilter</span>

:material-text-box: Filter articles from **identical authors** with **similar titles**<br>
:material-github: [`source code`]({{links.usecases}}/articles_similarity_filter.py){:target="\_blank"}
:material-package-variant-closed: `core.usecases`<br>
:material-file-code: `app/core/usecases/articles_similarity_filter.py`<br>

```py
class ArticlesSimilarityFilter()
```

From the `DataFrame` containing all the article information already gathered, the [authors are counted](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html){:target="\_blank"}, and those that were **repeated at least twice** are selected. Then, from the articles of these authors, their respective titles are selected and compared using the [TheFuzz `ratio()`](https://github.com/seatgeek/thefuzz?tab=readme-ov-file#simple-ratio){:target="\_blank"} function, and those whose **similarity rate** is at least `80%` are gathered and discarded.

!!! note

    After consideration and testing, we set the **similarity ratio** for the articles selection at `80%`.

For all the **similar articles** gathered, the first **one** is **kept** and the **rest** are **discarded**. If **all the authors are unique**, meaning **none are repeated**, or **no similar titles were found**, it will return the same `DataFrame`.

### <code class="badge-method"></code> <span class="code-method">filter</span>

```py
def filter(dataframe: DataFrame) -> DataFrame
```

Filters articles from the `DataFrame` if they are from **identical authors** with **similar titles**, and then all filtered data will be returned in a [Pandas `DataFrame`]({{links.dataframe}}){:target="\_blank"}.

| **Parameter** | **Type**    | **Description**                                                                |
| ------------- | ----------- | ------------------------------------------------------------------------------ |
| `dataframe`   | `DataFrame` | The `DataFrame` containing all the gathered article information to be filtered |

<br>
<!-- ScopusArticlesAggregator -->

## <code class="badge-class"></code> <span class="code-class">ScopusArticlesAggregator</span>

:material-text-box: Gathers, filters and compiles data from **Scopus** articles<br>
:material-github: [`source code`]({{links.usecases}}/scopus_articles_aggregator.py){:target="\_blank"}
:material-package-variant-closed: `core.usecases`<br>
:material-file-code: `app/core/usecases/scopus_articles_aggregator.py`<br>

```py
class ScopusArticlesAggregator(
    search_api: SearchAPI,
    abstract_api: AbstractAPI,
    similarity_filter: SimilarityFilter
)
```

First, articles are searched via **Scopus Search API** using the provided **search parameters**, and their **Scopus abstracts** are retrieved via **Scopus Abstract Retrieval API**.

Next, articles that are **exact duplicates** are removed, those with the **same authors and titles** are also discarded, and **similar articles** are filtered using [`ArticlesSimilarityFilter`](#articlessimilarityfilter).

An **error** is returned when [no articles are found](./responses-and-errors.md/#404-not-found).

| **Parameter**       | **Type**           | **Description**                                                                                                                                 |
| ------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_api`        | `SearchAPI`        | Injects [`ScopusSearchAPI`](#scopussearchapi) to search and get the articles via the **Scopus Search API**                                      |
| `articles_scraper`  | `abstract_api`     | Injects [`ScopusAbstractRetrievalAPI`](#scopusabstractretrievalapi) to retrieve the **Scopus abstracts** via the **ScopusAbstractRetrievalAPI** |
| `similarity_filter` | `SimilarityFilter` | Injects [`ArticlesSimilarityFilter`](#articlessimilarityfilter) to filter articles by **identical authors** with **similar titles**             |

### <code class="badge-method"></code> <span class="code-method">get_articles</span>

```py
def get_articles(params: SearchParams) -> FileResponse
```

Gathers and filters data from **Scopus articles**, writes and saves all remaining articles to a {{abbr.csv}} file, and returns them as a [FastAPI `FileResponse`]({{links.fastapiAdvanced}}/custom-response/?h=custom#fileresponse){:target="\_blank"} object.

| **Parameter** | **Type**       | **Description**                                              |
| ------------- | -------------- | ------------------------------------------------------------ |
| `params`      | `SearchParams` | The validated **API Key** and **Keywords** search parameters |

<br>
<!-- TemplateContextBuilder -->

## <code class="badge-class"></code> <span class="code-class">TemplateContextBuilder</span>

:material-text-box: Generates context values for template responses<br>
:material-github: [`source code`]({{links.presenters}}/template_context.py){:target="\_blank"}
:material-package-variant-closed: `adapters.presenters`<br>
:material-file-code: `app/adapters/presenters/template_context.py`<br>

```py
class TemplateContextBuilder(
    request: Request
)
```

Compiles and builds data, such as [context](https://jinja.palletsprojects.com/en/3.1.x/api/#the-context){:target="\_blank"} values, for the templates that [Jinja](https://jinja.palletsprojects.com/en/3.1.x/){:target="\_blank"} renders, passing them and loading them into {{abbr.html}} templates that are returned as a [Jinja2Templates `TemplateResponse`]({{links.fastapiAdvanced}}/templates/){:target="\_blank"} object.

| **Parameter** | **Type**  | **Description**                                                                                      |
| ------------- | --------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | `Request` | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |

### <code class="badge-method"></code> <span class="code-method">get_web_app_context</span>

```py
def get_web_app_context() -> Context
```

Returns data to build the {{abbr.api}} **web page** response template, returning the **request object**, **template name**, and **context values**.

About the **Context values**:

| **Field**     | **Description**                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |
| `version`     | Application version. **Example:** `2.0.0`                                                            |
| `repository`  | {{abbr.url}} of the application's **GitHub** repository                                              |
| `swagger_url` | Swagger page {{abbr.url}}. **Default:** `/`                                                          |
| `token`       | Application **Token**                                                                                |
| `filename`    | {{abbr.csv}} filename. **Default:** `articles.csv`                                                   |
| `table_url`   | Table web page {{abbr.url}}. **Default:** `/scopus-searcher/api/table`                               |
| `search_url`  | {{abbr.api}} {{abbr.url}}. **Default:** `/scopus-searcher/api/search-articles`                       |
| `description` | Application description                                                                              |

### <code class="badge-method"></code> <span class="code-method">get_table_context</span>

```py
def get_table_context() -> Context
```

Returns data to build the **Table web page** response template, returning the **request object**, **template name**, and **context values**.

About the **Context values**:

| **Field**     | **Description**                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |
| `version`     | Application version. **Example:** `2.0.0`                                                            |
| `repository`  | {{abbr.url}} of the application's **GitHub** repository                                              |
| `swagger_url` | Swagger page {{abbr.url}}. **Default:** `/`                                                          |
| `content`     | Table content. List of the articles found or `None` if there are no articles                         |
| `web_app_url` | Application web page {{abbr.url}}. **Default:** `/scopus-searcher/api`                               |

<br>
<!-- ExceptionJSON -->

## <code class="badge-class"></code> <span class="code-class">ExceptionJSON</span>

:material-text-box: Generates {{abbr.json}} representation responses for exceptions<br>
:material-github: [`source code`]({{links.presenters}}/exception_json.py){:target="\_blank"}
:material-package-variant-closed: `adapters.presenters`<br>
:material-file-code: `app/adapters/presenters/exception_json.py`<br>

```py
class ExceptionJSON(
    request: Request,
    code: int,
    message: str,
    errors: Errors = None
)
```

A **presenter** created using [FastAPI `JSONResponse`]({{links.fastapiAdvanced}}/custom-response/#jsonresponse){:target="\_blank"} that generates {{abbr.json}} representation responses for exceptions. The error details are filtered to remove the `PydanticUndefined` error from [Pydantic `ValidationError`](https://docs.pydantic.dev/latest/errors/errors/){:target="\_blank"} and the [`Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object data is retrieved.

The [datetime]({{links.pythonDocs}}/datetime.html){:target="\_blank"} timestamp is set as a `str` in [{{abbr.iso}} format](https://en.wikipedia.org/wiki/ISO_8601){:target="\_blank"} and finally all data is converted and encoded using the [FastAPI `jsonable_encoder()`]({{links.fastapiTutorial}}/encoder/){:target="\_blank"} function.

| **Parameter** | **Type**  | **Description**                                                                                      |
| ------------- | --------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | `Request` | The [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} object |
| `code`        | `int`     | {{abbr.http}} status error code                                                                      |
| `message`     | `str`     | Exception description                                                                                |
| `errors`      | `Errors`  | Error metadata and details                                                                           |

<br>
<!-- Exceptions and Errors -->

## Exceptions and Errors

{{abbr.http}} **Exceptions** are models built from [FastAPI `HTTPException`]({{links.fastapiTutorial}}/handling-errors/#use-httpexception){:target="\_blank"} that represent {{abbr.http}} **error** status codes sent in the response to notify the client using your application of an error. The ones implemented are [`401 Unauthorized`]({{links.mdnStatus}}/401){:target="\_blank"}, [`404 NotFound`]({{links.mdnStatus}}/404){:target="\_blank"}, [`422 UnprocessableContent`]({{links.mdnStatus}}/422){:target="\_blank"}, [`500 InternalError`]({{links.mdnStatus}}/500){:target="\_blank"}, [`502 BadGateway`]({{links.mdnStatus}}/502){:target="\_blank"} and [`504 GatewayTimeout`]({{links.mdnStatus}}/504){:target="\_blank"}.

**Application Errors** are models built from the [base class `Exception`]({{links.pythonDocs}}/exceptions.html#Exception){:target="\_blank"} that indicates that an **error** has occurred in the core part of the application's operation/processing. The ones implemented are [`InterruptError`]({{links.domain}}/exceptions.py){:target="\_blank"} for the **shutdown/exit interrupt signal** and [`ScopusAPIError`]({{links.domain}}/exceptions.py){:target="\_blank"} for the **Scopus Search API** {{abbr.http}} status error.

**Exception Handlers** are routines designed to process and respond quickly to the occurrence of **exceptions/errors** or specific special situations during the execution of a program, returning their {{abbr.json}} representation. The implemented handlers are for [Starlette `HTTPException`](https://www.starlette.io/exceptions/#httpexception){:target="\_blank"}, [FastAPI `HTTPException`]({{links.fastapiTutorial}}/handling-errors/#use-httpexception){:target="\_blank"}, [`RequestValidationError`]({{links.fastapiTutorial}}/handling-errors/#requestvalidationerror-vs-validationerror){:target="\_blank"}, [`ResponseValidationError`]({{links.fastapiTutorial}}/handling-errors/#requestvalidationerror-vs-validationerror){:target="\_blank"}, [`ValidationError`](https://docs.pydantic.dev/latest/errors/validation_errors/){:target="\_blank"}, [`HTTPException`]({{links.exceptions}}/http_exceptions.py){:target="\_blank"}, [`ApplicationError`]({{links.domain}}/exceptions.py){:target="\_blank"} and [`Exception`]({{links.pythonDocs}}/exceptions.html#Exception){:target="\_blank"}.

About the **Exception** {{abbr.json}} **Response**:

| **Field**   | **Type**        | **Description**                                                                            |
| ----------- | --------------- | ------------------------------------------------------------------------------------------ |
| `success`   | `bool`          | Result of the operation, which is a failure since it is an exception. **Deafult:** `False` |
| `code`      | `int`           | {{abbr.http}} error status code                                                            |
| `message`   | `str`           | Exception/error description                                                                |
| `request`   | `dict[str,Any]` | Contains some request data in a `dict`                                                     |
| `errors`    | `Errors`        | Contains some details of the exception/error in a `dict`. **Deafult:** `None`              |
| `timestamp` | `str`           | The datetime timestamp as a `str` in {{abbr.iso}} format                                   |

About the **`request` field**:

| **Field** | **Description**                                   |
| --------- | ------------------------------------------------- |
| `host`    | The request client host. **Default:** `127.0.0.1` |
| `port`    | The request client port. **Default:** `8000`      |
| `method`  | The request method                                |
| `url`     | The request {{abbr.url}} path                     |
| `headers` | The request headers                               |

About **`ScopusAPIError` error details**:

| **Field**   | **Description**                                                            |
| ----------- | -------------------------------------------------------------------------- |
| `status`    | The **Scopus APIs** {{abbr.http}} status error code                        |
| `api_error` | The **Scopus APIs** response status error description. **Deafult:** `null` |
| `content`   | The **Scopus APIs** {{abbr.json}} response content itself                  |

!!! note

    See the responses status error description in the [documentation]({{links.scSearchApi}}){:target="\_blank"}.

<br>
<!-- Middlewares -->

## Middlewares

**Middlewares** are mechanisms built on top of the [Starlette `BaseHTTPMiddleware`](https://www.starlette.io/middleware/#basehttpmiddleware){:target="\_blank"} that work in the application's **request-response cycle**, intercepting calls and processing them. They can access and manipulate each **request object** before it is processed by any route handlers, and also each **response object** before returning it. There are three implemented.

The [`TraceExceptionControl`]({{links.middleware}}/tracing_exception.py){:target="\_blank"} middleware **traces** the request, reporting the client, the {{abbr.url}} accessed, the response status code, and the processing time. It also **handles** any unexpected exceptions and signal-interrupt errors.

The [`RedirectNotFoundRoutes`]({{links.middleware}}/redirect_route.py){:target="\_blank"} middleware **redirects** any route not found request that receives a [`404 Not Found`]({{links.mdnStatus}}/404){:target="\_blank"} error and is not a mapped allowed route. It also **handles** signal-interrupt errors.

The [FastAPI `CORSMiddleware`]({{links.fastapiTutorial}}/cors/#use-corsmiddleware){:target="\_blank"} middleware implements and configures the [{{abbr.cors}} mechanism](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS){:target="\_blank"}, allowing any origin, any credentials, any header, and only the [`GET` method](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET){:target="\_blank"}.

<br>
<!-- SignalHandler -->

## <code class="badge-class"></code> <span class="code-class">SignalHandler</span>

:material-text-box: Set signal handlers to set the **shutdown event** flag<br>
:material-github: [`source code`]({{links.utils}}/signal_handler.py){:target="\_blank"}
:material-package-variant-closed: `utils`<br>
:material-file-code: `app/utils/signal_handler.py`<br>

```py
class SignalHandler(
    for_async: bool = None
)
```

Create an **event** object, either a [threading `Event`]({{links.pythonDocs}}/threading.html#event-objects){:target="\_blank"} or [asyncio `Event`]({{links.pythonDocs}}/asyncio-sync.html#asyncio.Event){:target="\_blank"} based on the **parameter** value, and register your handlers for the [`SIGINT`]({{links.pythonDocs}}/signal.html#signal.SIGINT){:target="\_blank"} and [`SIGTERM`]({{links.pythonDocs}}/signal.html#signal.SIGTERM){:target="\_blank"} signals using the [`signal()`]({{links.pythonDocs}}/signal.html#signal.signal){:target="\_blank"} function. The handlers will catch **shutdown signals** and set the **event flag**. Then, **process**-based or **threaded** operations can be terminated **gracefully**.

!!! info

    A **graceful shutdown** is a controlled and orderly process to perform a **safe shutdown** and free up resources when the application is suddenly interrupted or receives a shutdown/kill signal.

| **Parameter** | **Type** | **Description**                                                                  |
| ------------- | -------- | -------------------------------------------------------------------------------- |
| `for_async`   | `bool`   | Indicates whether the **event** will be asynchronous or not. **Default:** `None` |
