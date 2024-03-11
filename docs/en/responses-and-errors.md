# Responses and Errors

| Status Code | Response/Error        | Message                                                  | Description                                                   |
| :---------: | --------------------- | -------------------------------------------------------- | ------------------------------------------------------------- |
|     200     | List of dicts         | -                                                        | Articles found in the Scopus Search API                       |
|     200     | HTML template         | -                                                        | Article preview page in Scopus                                |
|     200     | HTML template         | -                                                        | Web Application                                               |
|     200     | CSV file              | -                                                        | Search results                                                |
|     400     | Bad Request           | Validation error in request/response                     | FastAPI validation error                                      |
|     401     | Unauthorized          | Invalid access token                                     | Access Token does not match what it expected                  |
|     401     | Unauthorized          | No access token provided                                 | -                                                             |
|     403     | Forbidden             | Missing ApiKey required query parameter                  | No ApiKey provided                                            |
|     404     | Not Found             | None articles has been found                             | Total search results are zero                                 |
|     422     | Unprocessable Content | Missing keywords required query parameter                | No keywords provided or all provided are empty                |
|     422     | Unprocessable Content | There must be at least two keywords                      | Keywords length shorter than the required two                 |
|     422     | Unprocessable Content | Invalid keyword                                          | Keyword does not match pattern                                |
|     422     | Scopus Api Error      | Invalid Response from Scopus API                         | **400**: Invalid information submitted                        |
|     422     | Scopus Api Error      | Invalid Response from Scopus API                         | **401**: Authentication error: missing or invalid credentials |
|     422     | Scopus Api Error      | Invalid Response from Scopus API                         | **403**: Authentication error: user cannot be validated       |
|     422     | Scopus Api Error      | Invalid Response from Scopus API                         | **429**: API key request quota limits exceeded                |
|     422     | Scopus Api Error      | Invalid Response from Scopus API                         | **500**: Internal error from Scopus API response              |
|     424     | Failed Dependency     | Request Connection Timeout                               | Got a Requests exception Timeout                              |
|     424     | Failed Dependency     | Connection Error in Request                              | Got a Requests exception Connection Error                     |
|     424     | Failed Dependency     | Unexpected Error from Request: ...                       | Got an unmapped exception                                     |
|     424     | Failed Dependency     | Unexpected status error ...                              | Got a client error status code in the response                |
|     424     | Failed Dependency     | Invalid Response from Scopus API                         | Response content is empty                                     |
|     424     | Failed Dependency     | Invalid Response from Article Page                       | An error occurred or the response content is empty            |
|     500     | Internal Error        | Error in decoding response from Scopus API               | JSON decode error                                             |
|     500     | Internal Error        | Pydantic validation error: ... validation errors for ... | Pydantic validation error                                     |
|     500     | Internal Error        | Unexpected Error ...                                     | Any unmapped exception                                        |
