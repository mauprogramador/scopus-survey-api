# Respostas e Erros

!!! tip

    Leia a documentação da {{abbr.mdn}} sobre o código de status de resposta {{abbr.http}} no [MDN Web Docs]({{links.mdnStatus}}){:target="\_blank"}.

## Bem-sucedida

### [`200 Ok`]({{links.mdnStatus}}/200){:target="\_blank"}

| **:material-routes: {{abbr.routePt}}** | **Resposta**                                         |
| -------------------------------------- | ---------------------------------------------------- |
| `/scopus-survey/api`                   | Renderiza a página web da {{abbr.api}} da aplicação  |
| `/scopus-survey/api/search-articles`   | Baixa o arquivo {{abbr.csv}} dos artigos encontrados |
| `/scopus-survey/api/table`             | Renderiza a página web da tabela de artigos          |

## Redirecionamento

### [`307 Temporary Redirect`]({{links.mdnStatus}}/307){:target="\_blank"}

Qualquer {{abbr.url}} de solicitação que não esteja na rota :material-routes: `/scopus-survey/api` será redirecionada para ela. Redireciona qualquer solicitação que esteja tentando acessar uma rota não encontrada/inexistente.

## Erro do cliente

### [`401 Unauthorized`]({{links.mdnStatus}}/401){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}** | **Descrição**                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------- |
| `Missing required API Key query parameter`                | _Query parameter_ obrigatório `API Key` não encontrado na solicitação |
| `Missing required Access Token header`                    | Cabeçalho obrigatório `Access Token` não encontrado na solicitação    |
| `Invalid Access Token`                                    | Cabeçalho `Access Token` tem um padrão inválido ou está incorreto     |

### [`404 Not Found`]({{links.mdnStatus}}/404){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}** | **Descrição**                                                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `No articles found`                                       | Nenhum artigo foi encontrado correspondendo às `Palavras-chave`.<br> O total de resultados da pesquisa é zero |

### [`422 Unprocessable Content`]({{links.mdnStatus}}/422){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}** | **Descrição**                                                                                                                      |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `Validation error in request <{...}>`                     | [Exceção FastAPI do Pydantic]({{links.fastapiValidationError}}){:target="\_blank"}.<br> A solicitação contém dados inválidos/erros |
| `Missing required Keywords query parameter`               | _Query parameter_ obrigatório `Palavras-chave` não encontrado na solicitação                                                       |
| `There must be at least two keywords`                     | O número de `Palavras-chave` está abaixo do mínimo necessário.<br> Submeta pelo menos duas `Palavras-chave` para realizar a busca  |
| `Invalid Keyword`                                         | A `Palavra-chave` submetida tem um padrão inválido                                                                                 |

## Erro do Servidor

### [`500 Internal Error`]({{links.mdnStatus}}/500){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}**  | **Descrição**                                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `Validation error in response <{...}>`                     | [Exceção FastAPI do Pydantic]({{links.fastapiValidationError}}){:target="\_blank"}.<br> A solicitação contém dados inválidos/erros    |
| `Pydantic validation error: ... validation errors for ...` | [Exceção do Pydantic]({{links.validationError}}){:target="\_blank"}.<br> Há um erro nos dados que estão sendo validados               |
| `Error in decoding response from Scopus API`               | Exceção {{abbr.json}}.<br> O corpo da resposta não contém {{abbr.json}} válido para decodificar                                       |
| `Error in validate response from Scopus API`               | Erro de [serialização]({{links.serialization}}){:target="\_blank"}.<br> A resposta {{abbr.json}} contém campos não mapeados/inválidos |
| `Unexpected application interruption`                      | Exceção de interrupção do [sinal de saída]({{links.pythonDocs}}/signal.html){:target="\_blank"} de desligamento                       |
| `Unexpected error <...>`                                   | Qualquer exceção não mapeada/comum                                                                                                    |

### [`502 Bad Gateway`]({{links.mdnStatus}}/502){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}** | **Descrição**                                                                |
| --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `Invalid response from Scopus Search API`                 | A resposta da **Scopus Search API** não tem conteúdo/dados                   |
| `Invalid response from Scopus Abstract Retrieval API`     | A resposta da **Scopus Abstract Retrieval API** não tem conteúdo/dados       |
| `Connection error in request`                             | Ocorreu um erro de conexão ao tentar enviar a solicitação                    |
| `Unexpected error from request <...>`                     | Ocorreu um erro/exceção não mapeado ao tentar enviar a solicitação           |
| `Invalid response from Scopus Search API`                 | Exceção de erro de status {{abbr.http}} da **Scopus Search API**             |
| `Invalid response from Scopus Abstract Retrieval API`     | Exceção de erro de status {{abbr.http}} da **Scopus Abstract Retrieval API** |

### [`504 Gateway Timeout`]({{links.mdnStatus}}/504){:target="\_blank"}

| **:material-code-json: Mensagem da {{abbr.exceptionPt}}** | **Descrição**                |
| --------------------------------------------------------- | ---------------------------- |
| `Request connection timeout`                              | A conexão solicitada expirou |

## Scopus APIs Status Error

!!! tip

    Leia a documentação sobre **respostas** para a [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"} e a [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}.

| **Código de Status** | **Descrição**                                                              |
| :------------------: | -------------------------------------------------------------------------- |
|       **400**        | Solicitação inválida. Informações enviadas inválidas                       |
|       **401**        | O usuário não pode ser autenticado devido a credenciais ausentes/inválidas |
|       **403**        | O usuário não pode ser autenticado ou os direitos não podem ser validados  |
|       **429**        | O solicitante excedeu os limites da cota associados ao sua `API Key`       |
|       **500**        | Erro de processamento interno da {{abbr.api}} **Scopus**                   |
