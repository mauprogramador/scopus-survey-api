# Responses and Errors

!!! tip

    Read the {{abbr.mdn}} documentation about the {{abbr.http}} response status code in [MDN Web Docs]({{links.mdnStatus}}){:target="\_blank"}.

## Successful

### [`200 Ok`]({{links.mdnStatus}}/200){:target="\_blank"}

| **:material-routes: {{abbr.route}}**   | **Response**                                      |
| -------------------------------------- | ------------------------------------------------- |
| `/scopus-searcher/api`                 | Renders the application {{abbr.api}} web page     |
| `/scopus-searcher/api/search-articles` | Downloads the {{abbr.csv}} file of found articles |
| `/scopus-searcher/api/table`           | Renders the articles table web page               |

## Redirection

### [`307 Temporary Redirect`]({{links.mdnStatus}}/307){:target="\_blank"}

Any request {{abbr.url}} that is not in the :material-routes: `/scopus-searcher/api` route will be redirected to it. Redirects any request that is trying to access a not found/non-existent route.

## Client Error

### [`401 Unauthorized`]({{links.mdnStatus}}/401){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message** | **Description**                                              |
| --------------------------------------------------- | ------------------------------------------------------------ |
| `Missing required API Key query parameter`          | Required `API Key` query parameter not found in the request  |
| `Missing required Access Token header`              | Required `Access Token` header not found in the request      |
| `Invalid Access Token`                              | `Access Token` header has an invalid pattern or is incorrect |

### [`404 Not Found`]({{links.mdnStatus}}/404){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message** | **Description**                                                                        |
| --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `No articles found`                                 | No articles were found matching the `Keywords`. <br> The total search results are zero |

### [`422 Unprocessable Content`]({{links.mdnStatus}}/422){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message** | **Description**                                                                                                                      |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `Validation error in request <{...}>`               | [FastAPI exception from Pydantic]({{links.fastapiValidationError}}){:target="\_blank"}.<br> The request contains invalid data/errors |
| `Missing required Keywords query parameter`         | Required `Keywords` query parameter not found in the request                                                                         |
| `There must be at least two keywords`               | The number of `Keywords` is below the minimum required.<br> Submit at least two `Keywords` to perform the search                     |
| `Invalid Keyword`                                   | The `Keyword` submitted has an invalid pattern                                                                                       |

## Server Error

### [`500 Internal Error`]({{links.mdnStatus}}/500){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message**        | **Description**                                                                                                                       |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `Validation error in response <{...}>`                     | [FastAPI exception from Pydantic]({{links.fastapiValidationError}}){:target="\_blank"}.<br> The response contains invalid data/errors |
| `Pydantic validation error: ... validation errors for ...` | [Pydantic exception]({{links.validationError}}){:target="\_blank"}.<br> There is an error in the data being validated                 |
| `Error in decoding response from Scopus API`               | {{abbr.json}} exception.<br> The response body does not contain valid {{abbr.json}} to decode                                         |
| `Error in validate response from Scopus API`               | [Serialization]({{links.serialization}}){:target="\_blank"} error.<br> {{abbr.json}} response contains unmapped/invalid fields        |
| `Unexpected application interruption`                      | Shutdown [signal exit]({{links.pythonDocs}}/signal.html){:target="\_blank"} interrupt exception                                       |
| `Unexpected error <...>`                                   | Any unmapped/common exception                                                                                                         |

### [`502 Bad Gateway`]({{links.mdnStatus}}/502){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message**   | **Description**                                                        |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| `Invalid response from Scopus Search API`             | Response from **Scopus Search API** has no content/data                |
| `Invalid response from Scopus Abstract Retrieval API` | Response from **Scopus Abstract Retrieval API** has no content/data    |
| `Connection error in request`                         | A connection error occurred while trying to send the request           |
| `Unexpected error from request <...>`                 | An unmapped error/exception occurred while trying to send the request  |
| `Invalid response from Scopus Search API`             | **Scopus Search API** {{abbr.http}} status error exception             |
| `Invalid response from Scopus Abstract Retrieval API` | **Scopus Abstract Retrieval API** {{abbr.http}} status error exception |

### [`504 Gateway Timeout`]({{links.mdnStatus}}/504){:target="\_blank"}

| **:material-code-json: {{abbr.exception}} Message** | **Description**                      |
| --------------------------------------------------- | ------------------------------------ |
| `Request connection timeout`                        | The request connection has timed out |

## Scopus APIs Status Error

!!! tip

    Read the documentation about **responses** for the [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"} and [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}.

| **Status code** | **Description**                                                             |
| :-------------: | --------------------------------------------------------------------------- |
|     **400**     | Invalid request. Invalid information submitted                              |
|     **401**     | User cannot be authenticated due to missing/invalid credentials             |
|     **403**     | User cannot be authenticated or entitlements cannot be validated            |
|     **429**     | The requester has exceeded the quota limits associated with their `API Key` |
|     **500**     | **Scopus** {{abbr.api}} internal processing error                           |
