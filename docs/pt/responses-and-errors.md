# Respostas e Erros

| Código de Status | Resposta/Erro         | Mensagem                                                 | Descrição                                                           |
| :--------------: | --------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- |
| 200              | Lista de dicionários  | -                                                        | Artigos encontrados na Scopus Search API                            |
| 200              | HTML template         | -                                                        | Página de visualização do artigo na Scopus                          |
| 200              | HTML template         | -                                                        | Applicação Web                                                      |
| 200              | Arquivo CSV           | -                                                        | Resultados da busca                                                 |
| 400              | Bad Request           | Validation error in request/response                     | Erro de validação do FastAPI                                        |
| 401              | Unauthorized          | Invalid access token                                     | Token de acesso não corresponde ao esperado                         |
| 401              | Unauthorized          | No access token provided                                 | Nenhum Token de acesso fornecido                                    |
| 403              | Forbidden             | Missing ApiKey required query parameter                  | Nenhuma ApiKey fornecida                                            |
| 404              | Not Found             | None articles has been found                             | O total de resultados da pesquisa é zero                            |
| 422              | Unprocessable Content | Missing keywords required query parameter                | Nenhuma palavra-chave fornecida ou todas as fornecidas estão vazias |
| 422              | Unprocessable Content | There must be at least two keywords                      | Comprimento das Palavras-chave é menor que os dois exigidos         |
| 422              | Unprocessable Content | Invalid keyword                                          | A Palavra-chave não corresponde ao padrão                           |
| 422              | Scopus Api Error      | Invalid Response from Scopus API                         | **400**: Informações inválidas enviadas                             |
| 422              | Scopus Api Error      | Invalid Response from Scopus API                         | **401**: Erro de autenticação: credenciais ausentes ou inválidas    |
| 422              | Scopus Api Error      | Invalid Response from Scopus API                         | **403**: Erro de autenticação: o usuário não pode ser validado      |
| 422              | Scopus Api Error      | Invalid Response from Scopus API                         | **429**: Limite da cota de solicitação da API key excedido          |
| 422              | Scopus Api Error      | Invalid Response from Scopus API                         | **500**: Erro interno na resposta da Scopus API                     |
| 424              | Failed Dependency     | Request Connection Timeout                               | Obteve uma exceção de tempo limite na requisição                    |
| 424              | Failed Dependency     | Connection Error in Request                              | Obteve uma exceção de erro na connexão da requisição                |
| 424              | Failed Dependency     | Unexpected Error from Request: ...                       | Obteve uma exceção não mapeada                                      |
| 424              | Failed Dependency     | Invalid Response from Scopus API                         | O conteúdo da resposta está vazio                                   |
| 424              | Failed Dependency     | Invalid Response from Article Page                       | Ocorreu um erro ou o conteúdo da resposta está vazio                |
| 500              | Internal Error        | Error in decoding response from Scopus API               | Erro na decodificação do JSON                                       |
| 500              | Internal Error        | Pydantic validation error: ... validation errors for ... | Erro de validação do Pydantic                                       |
| 500              | Internal Error        | Unexpected Error ...                                     | Qualquer exceção não mapeada                                        |
