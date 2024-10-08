# Referência

Aqui está o código ou referência da {{abbr.api}} Web, fornecendo detalhes sobre as classes, métodos, parâmetros, atributos e cada parte deste aplicação.

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

:material-text-box: Validador de tipo para parâmetros de busca **Chave da API** e **Palavras-chave**<br>
:material-github: [`código fonte`]({{links.common}}/types.py){:target="\_blank"}
:material-package-variant-closed: `core.common`<br>
:material-file-code: `app/core/common/types.py`<br>

```py
class SearchParams(
    api_key: str = Field(),
    keywords: Keywords = Field()
)
```

Um **validador** de modelo criado usando o [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} para os parâmetros **Chave da API** e **Palavras-chave** usados na busca da **Scopus Search API**, validando sua tipagem e valores usando a função [Pydantic `Field()`]({{links.field}}){:target="\_blank"}.

!!! note

    Leia mais sobre as regras e especificações da **Chave da API** e **Palavras-chave** na [seção de requisitos](./requirements.md).

| **Parâmetro** | **Tipo**   | **Descrição**                         |
| ------------- | ---------- | ------------------------------------- |
| `api_key`     | `str`      | Parâmetro de busca **Chave da API**   |
| `keywords`    | `Keywords` | Parâmetro de busca **Palavras-chave** |

<br>
<!-- ScopusResult -->

## <code class="badge-class"></code> <span class="code-class">ScopusResult</span>

:material-text-box: Serializador para o item do campo _entry_ no esquema {{abbr.json}} da resposta<br>
:material-github: [`código fonte`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusResult(
    link: str = Field(),
    url: str = Field()
    scopus_id: str = Field()
)
```

Um **serializador** de modelo criado usando o [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} para os itens da entrada na resposta da busca da **Scopus Search API**, convertendo-os para o código usando a função [Pydantic `Field()`]({{links.field}}){:target="\_blank"}.

| **Parâmetro** | **Tipo** | **Campo** {{abbr.json}} | **Descrição**                                      |
| ------------- | -------- | ----------------------- | -------------------------------------------------- |
| `link`        | `str`    | `@_fa`                  | Links de navegação no nível superior               |
| `url`         | `str`    | `prism:url`             | {{abbr.uri}} da **Content Abstract Retrieval API** |
| `scopus_id`   | `str`    | `dc:identifier`         | **ID Scopus** do artigo                            |

<br>
<!-- ScopusSearch -->

## <code class="badge-class"></code> <span class="code-class">ScopusSearch</span>

:material-text-box: Serializador para o esquema {{abbr.json}} da resposta da **Scopus Search API**<br>
:material-github: [`código fonte`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusSearch(
    total_results: int = Field(),
    items_per_page: int = Field(),
    entry: list[ScopusResult] = Field()
)
```

Um **serializador** de modelo construído usando o [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} para a resposta {{abbr.json}} da **Scopus Search API**, convertendo-a para o código usando a função [Pydantic `Field()`]({{links.field}}){:target="\_blank"}.

Antes da **validação**, ele acessará o campo {{abbr.json}} `search-results` para achatar a hierarquia e obter os dados reais.

!!! info

    Achatamento (*Flattening*) é o processo de transformar uma estrutura de dados {{abbr.json}} aninhada em um único nível de pares chave-valor.

| **Parâmetro**    | **Tipo**             | **Campo** {{abbr.json}}   | **Descrição**                                                    |
| ---------------- | -------------------- | ------------------------- | ---------------------------------------------------------------- |
| `total_results`  | `int`                | `opensearch:totalResults` | Número total de artigos encontrados                              |
| `items_per_page` | `int`                | `opensearch:itemsPerPage` | Número de artigos divididos em cada página                       |
| `entry`          | `list[ScopusResult]` | `entry`                   | Listas de dados dos artigos com os campos especificados na busca |

!!! note

    Leia mais sobre o [corpo {{abbr.json}} retornado e seus campos](./scopus-search-api.md/#response-body).

### <code class="badge-property"></code> <span class="code-property">pages_count</span>

```py
def pages_count() -> int
```

Calcula o **número de páginas** dividindo o **total de resultados** pelo número de **itens por página**, retornando o **menor `int`** usando a função [math `ceil()`]({{links.pythonDocs}}/math.html#math.ceil){:target="\_blank"}.

<br>
<!-- ScopusQuotaRateLimit -->

## <code class="badge-class"></code> <span class="code-class">ScopusQuotaRateLimit</span>

:material-text-box: Serializador para as respostas das **APIs da Scopus**<br>
:material-github: [`código fonte`]({{links.data}}/serializers.py){:target="\_blank"}
:material-package-variant-closed: `core.data`<br>
:material-file-code: `app/core/data/serializers.py`<br>

```py
class ScopusQuotaRateLimit(
    reset: float = Field(),
    status: str = Field(),
    error_code: str = Field()
)
```

Um **serializador** de modelo construído usando [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} para as respostas das **APIs da Scopus**, convertendo-as em código usando a função [Pydantic `Field()`]({{links.field}}){:target="\_blank"}.

Antes da **validação**, ele recuperará os cabeçalhos da resposta e obterá o campo {{abbr.json}} `error-response`, se presente.

| **Parâmetro** | **Tipo** | **Campo da Resposta** | **Descrição**                                                                 |
| ------------- | -------- | --------------------- | ----------------------------------------------------------------------------- |
| `reset`       | `float`  | `X-RateLimit-Reset`   | Data/hora em **Epoch** segundos quando a cota da {{abbr.api}} será redefinida |
| `status`      | `str`    | `X-ELS-Status`        | Status da **Scopus** {{abbr.api}}/servidor Elsevier                           |
| `error_code`  | `str`    | `error-code`          | Código de erro da **Scopus** {{abbr.api}}/servidor Elsevier                   |

!!! info

    [Epoch](https://en.wikipedia.org/wiki/Epoch_(computing)){:target="\_blank"} é o número de segundos que se passaram desde 1º de janeiro de 1970, também conhecido como [tempo Unix](https://en.wikipedia.org/wiki/Unix_time){:target="\_blank"}.

### <code class="badge-property"></code> <span class="code-property">reset_datetime</span>

```py
def reset_datetime() -> str
```

Converte a **data e hora da epoch** do **cabeçalho de redefinição de cota** para `datetime`, formate-o e retorne-o como uma `str` mais compreensível da data e hora, informando quando a **cota de solicitação da** {{abbr.api}} será redefinida.

### <code class="badge-property"></code> <span class="code-property">quota_exceeded</span>

```py
def quota_exceeded() -> int
```

Verifique o valor do **cabeçalho de status** da resposta, retornando `True` se for igual a `QUOTA_EXCEEDED - Quota Exceeded` ou `False` caso contrário.

!!! note

    Saiba mais sobre o [limite de cota de solicitações de {{abbr.api}}]({{links.scApiKey}}){:target="\_blank"}.

### <code class="badge-property"></code> <span class="code-property">rate_limit_exceeded</span>

```py
def rate_limit_exceeded() -> bool
```

Verifique o valor do **campo de código de erro** da resposta, retornando `True` se for igual a `RATE_LIMIT_EXCEEDED` ou `False` caso contrário.

!!! note

    Saiba mais sobre o [limite da taxa de limitação de solicitação da {{abbr.api}}]({{links.scApiKey}}){:target="\_blank"}.

<br>
<!-- ScopusAbstract -->

## <code class="badge-class"></code> <span class="code-class">ScopusAbstract</span>

:material-text-box: Serializador para o esquema {{abbr.json}} da resposta da **Scopus Abstract Retrieval API**<br>
:material-github: [`código fonte`]({{links.data}}/serializers.py){:target="\_blank"}
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

Um **serializador** de modelo construído usando o [Pydantic `BaseModel`]({{links.baseModel}}){:target="\_blank"} para os **resumos Scopus** dos artigos na resposta {{abbr.json}}, convertendo-os em código usando a função [Pydantic `Field()`]({{links.field}}){:target="\_blank"} e definindo `null` para todos os campos que não forem retornados.

Antes da **validação**, a hierarquia será achatada para obter os dados reais. Primeiro, o campo {{abbr.json}} `abstracts-retrieval-response` será acessado, então o campo `authors` será definido a partir do campo {{abbr.json}} `author`, obtido do campo {{abbr.json}} `authors` se retornado ou do campo {{abbr.json}} `dc:creator` caso contrário.

!!! info

    Achatamento (*Flattening*) é o processo de transformar uma estrutura de dados {{abbr.json}} aninhada em um único nível de pares chave-valor.

Além disso, os **nomes dos autores** serão selecionados do campo {{abbr.json}} `ce:indexed-name` dos dados do autor, para serem concatenados e retornados. Finalmente, o campo {{abbr.json}} `coredata` será acessado e atualizado com os dados do autor antes de retorná-los.

Quando desserializado em `dict`, o campo `date`, quando não `null`, será formatado como `DD-MM-AAAA`.

| **Parâmetro**      | **Tipo** | **Campo** {{abbr.json}}   | **Descrição**                                        |
| ------------------ | -------- | ------------------------- | ---------------------------------------------------- |
| `url`              | `str`    | `link ref=scopus`         | URL da página de visualização do artigo do Scopus    |
| `scopus_id`        | `str`    | `dc:identifier`           | ID Scopus do artigo                                  |
| `authors`          | `str`    | `authors` or `dc:creator` | Lista completa de autores ou apenas o primeiro autor |
| `title`            | `str`    | `dc:title`                | Título do artigo                                     |
| `publication_name` | `str`    | `prism:publicationName`   | Título da fonte                                      |
| `abstract`         | `str`    | `dc:description`          | Resumo completo do artigo                            |
| `date`             | `str`    | `prism:coverDate`         | Data de publicação                                   |
| `eid`              | `str`    | `eid`                     | ID Eletrônico do artigo                              |
| `doi`              | `str`    | `prism:doi`               | Identificador de Objeto do Documento                 |
| `volume`           | `str`    | `prism:volume`            | Identificador para uma publicação em série           |
| `citations`        | `str`    | `citedby-count`           | Contagem de citações                                 |

!!! note

    Leia mais sobre os campos retornados na [documentação do Scopus Search Views](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"}.

<br>
<!-- AccessToken -->

## <code class="badge-class"></code> <span class="code-class">AccessToken</span>

:material-text-box: Obtém e valida o {{abbr.token}} **de Acesso**<br>
:material-github: [`código fonte`]({{links.dependencies}}/access_token.py){:target="\_blank"}
:material-package-variant-closed: `framework.dependencies`<br>
:material-file-code: `app/framework/dependencies/access_token.py`<br>

```py
class AccessToken()(
    request: Request,
    access_token: Annotated[str | None, TokenHeader] = None
)
```

Uma [dependência]({{links.fastapiTutorial}}/dependencies/){:target="\_blank"} de rota que implementa o método `__call__` para criar uma [instância chamável](https://realpython.com/python-callable-instances/){:target="\_blank"} que obterá e validará o cabeçalho {{abbr.token}} **de Acesso** por meio da função [FastAPI `Header()`]({{links.fastapiTutorial}}/header-params/){:target="\_blank"} ou da solicitação.

Para fornecer um pouco mais de segurança, o aplicaçaõ **gerará automaticamente** um {{abbr.token}} que será passado para a página web da {{abbr.api}} da aplicação, que por sua vez o enviará no **cabeçalho da solicitação** para **validação**.

| **Parâmetro**  | **Tipo**        | **Descrição**                                                                                      |
| -------------- | --------------- | -------------------------------------------------------------------------------------------------- |
| `request`      | `Request`       | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} |
| `access_token` | `str` or `None` | Descritor e validador do cabeçalho {{abbr.token}} da solicitação. **Default:** `None`              |

<br>
<!-- QueryParams -->

## <code class="badge-class"></code> <span class="code-class">QueryParams</span>

:material-text-box: Obtém e valida os {{abbr.queryParams}}**s**<br>
:material-github: [`código fonte`]({{links.dependencies}}/query_params.py){:target="\_blank"}
:material-package-variant-closed: `framework.dependencies`<br>
:material-file-code: `app/framework/dependencies/query_params.py`<br>

```py
class QueryParams()(
    request: Request,
    api_key: Annotated[str | None, APIKeyQuery] = None,
    keywords: Annotated[Keywords | None, KeywordsQuery] = None
)
```

Uma [dependência]({{links.fastapiTutorial}}/dependencies/){:target="\_blank"} de rota que implementa o método `__call__` para criar uma [instância chamável](https://realpython.com/python-callable-instances/){:target="\_blank"} que obterá e validará os parâmetros de consulta **Chave da API** e **Palavras-chave** por meio da função [FastAPI `Query()`]({{links.fastapiTutorial}}/query-params-str-validations/){:target="\_blank"} ou da solicitação.

| **Parâmetro** | **Tipo**             | **Descrição**                                                                                        |
| ------------- | -------------------- | ---------------------------------------------------------------------------------------------------- |
| `request`     | `Request`            | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"}   |
| `api_key`     | `str` or `None`      | Descritor e validador do {{abbr.queryParams}} da solicitação **Chave da API**. **Default:** `None`   |
| `keywords`    | `Keywords` or `None` | Descritor e validador do {{abbr.queryParams}} da solicitação **Palavras-chave**. **Default:** `None` |

### <code class="badge-method"></code> <span class="code-method">equals</span>

```py
def equals(api_key: str, keywords: list[str]) -> bool
```

Compara a **Chave da API** e as **Palavras-chave** da instância com outra **Chave de API** e **Palavras-chave**, retorna `True` se forem iguais ou `False` caso contrário.

| **Parâmetro** | **Tipo**    | **Descrição**                    |
| ------------- | ----------- | -------------------------------- |
| `api_key`     | `str`       | **Chave da API** para comparação |
| `keywords`    | `list[str]` | **Keywords** para comparação     |

### <code class="badge-method"></code> <span class="code-method">to_dict</span>

```py
def to_dict() -> dict[str, str | Keywords]
```

Serializa os atributos de instância **Chave da API** e **Palavras-chave** como um `dict`.

<br>
<!-- HTTPRetryHelper -->

## <code class="badge-class"></code> <span class="code-class">HTTPRetryHelper</span>

:material-text-box: Faça solicitações {{abbr.http}} com mecanismos de {{abbr.throttling}} e {{abbr.retry}}<br>
:material-github: [`código fonte`]({{links.helpers}}/http_retry_helper.py){:target="\_blank"}
:material-package-variant-closed: `adapters.helpers`<br>
:material-file-code: `app/adapters/helpers/http_retry_helper.py`<br>

```py
class HTTPRetryHelper(
    for_search: bool = None
)
```

Um [cliente](<https://en.wikipedia.org/wiki/Client_(computing)>){:target="\_blank"} {{abbr.http}} para fazer solicitações com os seguintes mecanismos:

- [Throttling](https://www.tibco.com/glossary/what-is-api-throttling){:target="\_blank"}: controla a taxa de fluxo de dados em um serviço limitando o número de solicitações da {{abbr.api}} que um usuário pode fazer em um determinado período.
- [Retry](https://medium.com/@API4AI/best-practice-implementing-retry-logic-in-http-api-clients-0b5469c08ced){:target="\_blank"}: tenta novamente operações com falha automaticamente para se recuperar de falhas inesperadas e continuar funcionando corretamente.
- [Rate Limiting](https://www.enjoyalgorithms.com/blog/throttling-and-rate-limiting){:target="\_blank"}: limita o tráfego da rede controlando o número de solicitações que podem ser feitas em um determinado período de tempo.
- [Session]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"}: persiste certos parâmetros e reutiliza a mesma conexão em todas as solicitações.
- [Cache](<https://en.wikipedia.org/wiki/Cache_(computing)>){:target="\_blank"}: armazena dados temporariamente para que futuras solicitações desses dados possam ser atendidas mais rapidamente.

| **Parâmetro** | **Tipo** | **Descrição**                                                                                                        |
| ------------- | -------- | -------------------------------------------------------------------------------------------------------------------- |
| `for_search`  | `bool`   | Indica na mensagem do log se a solicitação será direcionada para a **Scopus Search API** ou não. **Default:** `None` |

### <code class="badge-method"></code> <span class="code-method">mount_session</span>

```py
def mount_session(headers: Headers) -> None
```

Inicializa a [sessão]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"} e a monta registrando o adaptador de conexão de [controle de cache]({{links.pypi}}/CacheControl/){:target="\_blank"} com a configuração de [retry](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry){:target="\_blank"}.

| **Parâmetro** | **Tipo**  | **Descrição**                                          |
| ------------- | --------- | ------------------------------------------------------ |
| `headers`     | `Headers` | Os cabeçalhos {{abbr.http}} para enviar na solicitação |

### <code class="badge-method"></code> <span class="code-method">close</span>

```py
def close() -> None
```

Fecha o adaptador de conexão de [controle de cache]({{links.pypi}}/CacheControl/){:target="\_blank"} e a [sessão]({{links.requestsDocs}}/user/advanced/#session-objects){:target="\_blank"}.

### <code class="badge-method"></code> <span class="code-method">request</span>

```py
def request(url: str) -> Response
```

Inicializa, [prepara com sessão]({{links.requestsDocs}}/user/advanced/#prepared-requests){:target="\_blank"}, envia a solicitação, e então retorna a resposta como um objeto [Requests `Response`]({{links.requestsDocs}}/api/#requests.Response){:target="\_blank"}.

| **Parâmetro** | **Tipo** | **Descrição**                            |
| ------------- | -------- | ---------------------------------------- |
| `url`         | `str`    | A {{abbr.url}} para enviar a solicitação |

<br>
<!-- URLBuilderHelper -->

## <code class="badge-class"></code> <span class="code-class">URLBuilderHelper</span>

:material-text-box: Gera e formata {{abbr.url}}s para as solicitações {{abbr.http}}<br>
:material-github: [`código fonte`]({{links.helpers}}/url_builder_helper.py){:target="\_blank"}
:material-package-variant-closed: `adapters.helpers`<br>
:material-file-code: `app/adapters/helpers/url_builder_helper.py`<br>

```py
class URLBuilderHelper()
```

Um construtor para gerar as {{abbr.url}}s de recursos das **APIs da Scopus** e a {{abbr.url}} de [paginação](https://en.wikipedia.org/wiki/Pagination){:target="\_blank"}.

### <code class="badge-method"></code> <span class="code-method">get_search_url</span>

```py
def get_search_url(keywords: Keywords) -> str
```

Gera a {{abbr.url}} do recurso da **Scopus Search API** e a retorna como `str`.

| **Parâmetro** | **Tipo**   | **Descrição**                                       |
| ------------- | ---------- | --------------------------------------------------- |
| `keywords`    | `Keywords` | As **Palavras-chave** que serão utilizadas na busca |

### <code class="badge-method"></code> <span class="code-method">get_pagination_url</span>

```py
def get_pagination_url(page: int) -> str
```

Gera a {{abbr.url}} de paginação da **Scopus Search API** e a retorna como `str`.

| **Parâmetro** | **Tipo** | **Descrição**                                 |
| ------------- | -------- | --------------------------------------------- |
| `page`        | `int`    | O índice de página para o início da paginação |

### <code class="badge-method"></code> <span class="code-method">get_article_page_url</span>

```py
def get_abstract_url(url: str) -> str
```

Gera a {{abbr.url}} do recurso da **Scopus Abstract Retrieval API** e a retorna como `str`.

| **Parâmetro** | **Tipo** | **Descrição**                                                       |
| ------------- | -------- | ------------------------------------------------------------------- |
| `url`         | `str`    | A {{abbr.url}} do recurso base da **Scopus Abstract Retrieval API** |

<br>
<!-- ScopusSearchAPI -->

## <code class="badge-class"></code> <span class="code-class">ScopusSearchAPI</span>

:material-text-box: Busca e recupera artigos por meio da **Scopus Search API**<br>
:material-github: [`código fonte`]({{links.gateway}}/scopus_search_api.py){:target="\_blank"}
:material-package-variant-closed: `adapters.gateway`<br>
:material-file-code: `app/adapters/gateway/scopus_search_api.py`<br>

```py
class ScopusSearchAPI(
    http_helper: HttpRetry,
    url_builder: UrlBuilder
)
```

Primeiro, os cabeçalhos da solicitação para a **API da Scopus** serão construídos com a `Chave da API`, a [{{abbr.url}} do recurso](./scopus-search-api.md/#api-resource-url) é construída com a `Chave da API` e `Palavras-chave` como parâmetros de pesquisa, e então os artigos serão buscados por meio da **Scopus Search API**. Em seguida, a resposta é validada, recuperando os artigos se bem-sucedida ou lidando com erros caso contrário.

Um **erro** será retornado quando: [nenhum artigo for encontrado](./responses-and-errors.md/#404-not-found), a [cota da `Chave da API` for excedida](./api-limit-and-fields-and-filter.md/#quota-exceeded), a **Scopus Search API** retornar um [erro de status {{abbr.http}}](./responses-and-errors.md/#scopus-apis-status-error), e quando a [resposta {{abbr.json}}](./scopus-search-api.md/#response-body) não puder ser validada.

!!! note

    Saiba mais sobre a [cota de quantos dados uma **Chave da API** pode recuperar]({{links.scApiKey}}){:target="\_blank"}.

Os dados dos artigos serão validados, assumindo como padrão `null` para os campos que não forem retornados. Ele pode usar [threads](https://realpython.com/intro-to-python-threading/#what-is-a-thread){:target="\_blank"} com o [ThreadPoolExecutor]({{links.pythonDocs}}/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor){:target="\_blank"} e construir a {{abbr.url}} com o **índice da página** quando houver vários artigos para buscar com [paginação](https://en.wikipedia.org/wiki/Pagination){:target="\_blank"}.

| **Parâmetro** | **Tipo**     | **Descrição**                                                                    |
| ------------- | ------------ | -------------------------------------------------------------------------------- |
| `http_helper` | `HttpRetry`  | Injeta o [`HttpRetryHelper`](#httpretryhelper) para fazer as solicitações        |
| `url_builder` | `UrlBuilder` | Injeta o [`UrlBuilderHelper`](#urlbuilderhelper) para construir as {{abbr.url}}s |

### <code class="badge-method"></code> <span class="code-method">search_articles</span>

```py
def search_articles(search_params: SearchParams) -> list[ScopusResult]
```

Busca artigos por meio da **Scopus Search API**, compila e retorna todos os dados recuperados em uma `list` de [`ScopusResult`](#scopusresult){:target="\_blank"}.

| **Parâmetro**   | **Tipo**       | **Descrição**                                                      |
| --------------- | -------------- | ------------------------------------------------------------------ |
| `search_params` | `SearchParams` | Parâmetros de pesquisa `Chave de API` e `Palavras-chave` validados |

<br>
<!-- ScopusAbstractRetrievalAPI -->

## <code class="badge-class"></code> <span class="code-class">ScopusAbstractRetrievalAPI</span>

:material-text-box: Recupera **resumos Scopus** por meio da **Scopus Abstract Retrieval API**<br>
:material-github: [`código fonte`]({{links.gateway}}/scopus_abstract_retrieval_api.py){:target="\_blank"}
:material-package-variant-closed: `adapters.gateway`<br>
:material-file-code: `app/adapters/gateway/scopus_abstract_retrieval_api.py`<br>

```py
class ScopusAbstractRetrievalAPI(
    http_helper: HttpRetry,
    url_builder: UrlBuilder
)
```

Primeiro, os cabeçalhos da solicitação para a **API da Scopus** serão criados com a `Chave da API`, a [{{abbr.url}} do recurso](./scopus-abstract-retrieval-api.md/#final-url) é criada a partir da [{{abbr.url}} do recurso](./scopus-abstract-retrieval-api.md/#final-url) base e, em seguida, os **resumos Scopus** serão recuperados por meio da **Scopus Abstracts Retrieval API**. A resposta é então validada, recuperando os resumos se bem-sucedida ou manipulando erros caso contrário.

Um **erro** será retornado quando: a [cota da `Chave da API` for excedida](./api-limit-and-fields-and-filter.md/#quota-exceeded), a **Scopus Abstract Retrieval API** retornar um [erro de status {{abbr.http}}](./responses-and-errors.md/#scopus-apis-status-error), e quando a [resposta {{abbr.json}}](./scopus-abstract-retrieval-api.md/#response-body) não puder ser validada.

Os dados dos resumos serão validados, assumindo como padrão `null` para os campos que não forem retornados. Ele pode usar [threads](https://realpython.com/intro-to-python-threading/#what-is-a-thread){:target="\_blank"} com o [ThreadPoolExecutor]({{links.pythonDocs}}/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor){:target="\_blank"} quando houver vários resumos para recuperar.

| **Parâmetro** | **Tipo**     | **Descrição**                                                                    |
| ------------- | ------------ | -------------------------------------------------------------------------------- |
| `http_helper` | `HttpRetry`  | Injeta o [`HttpRetryHelper`](#httpretryhelper) para fazer as solicitações        |
| `url_builder` | `UrlBuilder` | Injeta o [`UrlBuilderHelper`](#urlbuilderhelper) para construir as {{abbr.url}}s |

### <code class="badge-method"></code> <span class="code-method">retrieve_abstracts</span>

```py
def retrieve_abstracts(api_key: str, entry: list[ScopusResult]) -> DataFrame
```

Recupera **resumos Scopus** por meio da **Scopus Abstract Retrieval API**, compila e retorna todos os dados buscados em um [Pandas `DataFrame`]({{links.dataframe}}){:target="\_blank"}.

| **Parâmetro** | **Tipo**             | **Descrição**                                 |
| ------------- | -------------------- | --------------------------------------------- |
| `api_key`     | `str`                | Parâmetro de pesquisa `Chave de API` validado |
| `entry`       | `list[ScopusResult]` | Lista dos dados dos artigos                   |

<br>
<!-- ArticlesSimilarityFilter -->

## <code class="badge-class"></code> <span class="code-class">ArticlesSimilarityFilter</span>

:material-text-box: Filtrar artigos de **autores idênticos** com **títulos semelhantes**<br>
:material-github: [`código fonte`]({{links.usecases}}/articles_similarity_filter.py){:target="\_blank"}
:material-package-variant-closed: `core.usecases`<br>
:material-file-code: `app/core/usecases/articles_similarity_filter.py`<br>

```py
class ArticlesSimilarityFilter()
```

Do `DataFrame` contendo todas as informações dos artigos já coletadas, os [autores são contados](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html){:target="\_blank"}, e aqueles que foram **repetidos pelo menos duas vezes** são selecionados. Então, dos artigos desses autores, seus respectivos títulos são selecionados e comparados usando a função [TheFuzz `ratio()`](https://github.com/seatgeek/thefuzz?tab=readme-ov-file#simple-ratio){:target="\_blank"}, e aqueles cuja **taxa de similaridade** é de pelo menos `80%` são coletados e descartados.

!!! note

    Após consideração e testes, definimos a **taxa de similaridade** para a seleção de artigos em `80%`.

Para todos os **artigos semelhantes** reunidos, o **primeiro** é **mantido** e o **restante** é **descartado**. Se **todos os autores forem únicos**, ou seja, **nenhum é repetido**, ou **nenhum título semelhante foi encontrado**, ele retornará o mesmo `DataFrame`.

### <code class="badge-method"></code> <span class="code-method">filter</span>

```py
def filter(dataframe: DataFrame) -> DataFrame
```

Filtra artigos do `DataFrame` se eles forem de **autores idênticos** com **títulos semelhantes**, e então todos os dados filtrados serão retornados em um [Pandas `DataFrame`]({{links.dataframe}}){:target="\_blank"}.

| **Parâmetro** | **Tipo**    | **Descrição**                                                                     |
| ------------- | ----------- | --------------------------------------------------------------------------------- |
| `dataframe`   | `DataFrame` | O `DataFrame` contendo todas as informações do artigo coletadas a serem filtradas |

<br>
<!-- ScopusArticlesAggregator -->

## <code class="badge-class"></code> <span class="code-class">ScopusArticlesAggregator</span>

:material-text-box: Reúne, filtra e compila dados de artigos **Scopus**<br>
:material-github: [`código fonte`]({{links.usecases}}/scopus_articles_aggregator.py){:target="\_blank"}
:material-package-variant-closed: `core.usecases`<br>
:material-file-code: `app/core/usecases/scopus_articles_aggregator.py`<br>

```py
class ScopusArticlesAggregator(
    search_api: SearchAPI,
    abstract_api: AbstractAPI,
    similarity_filter: SimilarityFilter
)
```

Primeiro, os artigos são pesquisados por meio da **Scopus Search API** usando os **parâmetros de busca** fornecidos, e seus **resumos Scopus** são recuperados por meio da **Scopus Abstract Retrieval API**.

Em seguida, os artigos que são **duplicatas exatas** são removidos, aqueles com os **mesmos autores e títulos** também são descartados, e **artigos semelhantes** são filtrados usando [`ArticlesSimilarityFilter`](#articlessimilarityfilter).

Um **erro** é retornado quando [nenhum artigo é encontrado](./responses-and-errors.md/#404-not-found).

| **Parâmetro**       | **Tipo**           | **Descrição**                                                                                                                                        |
| ------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_api`        | `SearchAPI`        | Injeta o [`ScopusSearchAPI`](#scopussearchapi) para pesquisar e obter os artigos por meio da **Scopus Search API**                                   |
| `articles_scraper`  | `abstract_api`     | Injeta o [`ScopusAbstractRetrievalAPI`](#scopusabstractretrievalapi) para recuperar os **resumos Scopus** por meio da **ScopusAbstractRetrievalAPI** |
| `similarity_filter` | `SimilarityFilter` | Injeta o [`ArticlesSimilarityFilter`](#articlessimilarityfilter) para filtrar os artigos de **autores idênticos** com **títulos semelhantes**        |

### <code class="badge-method"></code> <span class="code-method">get_articles</span>

```py
def get_articles(params: SearchParams) -> FileResponse
```

Reúne e filtra dados de **artigos Scopus**, grava e salva todos os artigos restantes em um arquivo {{abbr.csv}} e os retorna como um objeto [FastAPI `FileResponse`]({{links.fastapiAdvanced}}/custom-response/?h=custom#fileresponse){:target="\_blank"}.

| **Parâmetro** | **Tipo**       | **Descrição**                                                       |
| ------------- | -------------- | ------------------------------------------------------------------- |
| `params`      | `SearchParams` | Parâmetros de busca **Chave da API** e **Palavras-chave** validados |

<br>
<!-- TemplateContextBuilder -->

## <code class="badge-class"></code> <span class="code-class">TemplateContextBuilder</span>

:material-text-box: Gera valores de contexto para respostas de _template_<br>
:material-github: [`código fonte`]({{links.presenters}}/template_context.py){:target="\_blank"}
:material-package-variant-closed: `adapters.presenters`<br>
:material-file-code: `app/adapters/presenters/template_context.py`<br>

```py
class TemplateContextBuilder(
    request: Request
)
```

Compila e cria dados, como valores de [contexto](https://jinja.palletsprojects.com/en/3.1.x/api/#the-context){:target="\_blank"}, para os _templates_ que o [Jinja](https://jinja.palletsprojects.com/en/3.1.x/){:target="\_blank"} renderiza, passando-os e carregando-os em _templates_ {{abbr.html}} que são retornados como um objeto [Jinja2Templates `TemplateResponse`]({{links.fastapiAdvanced}}/templates/){:target="\_blank"}.

| **Parâmetro** | **Tipo**  | **Descrição**                                                                                      |
| ------------- | --------- | -------------------------------------------------------------------------------------------------- |
| `request`     | `Request` | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} |

### <code class="badge-method"></code> <span class="code-method">get_web_app_context</span>

```py
def get_web_app_context() -> Context
```

Retorna dados para construir o _template_ da resposta da **página web da** {{abbr.api}}, retornando o **objeto da solicitação**, o **nome do _template_**, e os **valores de contexto**.

Sobre os **valores do Contexto**:

| **Campo**     | **Descrição**                                                                                      |
| ------------- | -------------------------------------------------------------------------------------------------- |
| `request`     | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} |
| `version`     | Versão da aplicação. **Exemplo:** `3.0.0`                                                          |
| `repository`  | {{abbr.url}} do repositório **GitHub** da aplicação                                                |
| `swagger_url` | {{abbr.url}} da página do **Swagger**. **Default:** `/`                                            |
| `token`       | **Token** da aplicação                                                                             |
| `filename`    | Nome do arquivo {{abbr.csv}}. **Default:** `articles.csv`                                          |
| `table_url`   | {{abbr.url}} da página web da tabela. **Default:** `/scopus-survey/api/table`                      |
| `search_url`  | {{abbr.url}} da {{abbr.api}}. **Default:** `/scopus-survey/api/search-articles`                    |
| `description` | Descrição da aplicação                                                                             |

### <code class="badge-method"></code> <span class="code-method">get_table_context</span>

```py
def get_table_context() -> Context
```

Retorna dados para construir o _template_ da resposta da **página web da Tabela**, retornando o **objeto da solicitação**, o **nome do _template_**, e os **valores de contexto**.

Sobre os **valores do Contexto**:

| **Campo**     | **Descrição**                                                                                      |
| ------------- | -------------------------------------------------------------------------------------------------- |
| `request`     | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} |
| `version`     | Versão da aplicação. **Exemplo:** `3.0.0`                                                          |
| `repository`  | {{abbr.url}} do repositório **GitHub** da aplicação                                                |
| `swagger_url` | {{abbr.url}} da página do **Swagger**. **Default:** `/`                                            |
| `content`     | Conteúdo da tabela. Lista dos artigos encontrados ou `None` se não houver artigos                  |
| `web_app_url` | {{abbr.url}} da página web da aplicação. **Default:** `/scopus-survey/api`                         |

<br>
<!-- ExceptionJSON -->

## <code class="badge-class"></code> <span class="code-class">ExceptionJSON</span>

:material-text-box: Gera respostas de representação {{abbr.json}} para exceções<br>
:material-github: [`código fonte`]({{links.presenters}}/exception_json.py){:target="\_blank"}
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

Um **_presenter_** criado usando [FastAPI `JSONResponse`]({{links.fastapiAdvanced}}/custom-response/#jsonresponse){:target="\_blank"} que gera respostas de representação {{abbr.json}} para exceções. Os detalhes do erro são filtrados para remover o erro `PydanticUndefined` de [Pydantic `ValidationError`](https://docs.pydantic.dev/latest/errors/errors/){:target="\_blank"} e os dados do objeto [`Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} são recuperados.

O _timestamp_ [datetime]({{links.pythonDocs}}/datetime.html){:target="\_blank"} é definido como uma `str` no [formato {{abbr.iso}}](https://en.wikipedia.org/wiki/ISO_8601){:target="\_blank"} e, finalmente, todos os dados são convertidos e codificados usando a função [FastAPI `jsonable_encoder()`]({{links.fastapiTutorial}}/encoder/){:target="\_blank"}.

| **Parâmetro** | **Tipo**  | **Descrição**                                                                                      |
| ------------- | --------- | -------------------------------------------------------------------------------------------------- |
| `request`     | `Request` | O objeto [FastAPI `Request`]({{links.fastapiAdvanced}}/using-request-directly/){:target="\_blank"} |
| `code`        | `int`     | Código de erro de status {{abbr.http}}                                                             |
| `message`     | `str`     | Descrição da exceção                                                                               |
| `errors`      | `Errors`  | Metadados e detalhes do erro                                                                       |

<br>
<!-- Exceções e Erros -->

## Exceções e Erros

**Exceções** {{abbr.http}} são modelos criados a partir do [FastAPI `HTTPException`]({{links.fastapiTutorial}}/handling-errors/#use-httpexception){:target="\_blank"} que representam códigos de status de **erro** {{abbr.http}} enviados na resposta para notificar o cliente usando sua aplicação de um erro. Os implementados são [`401 Unauthorized`]({{links.mdnStatus}}/401){:target="\_blank"}, [`404 NotFound`]({{links.mdnStatus}}/404){:target="\_blank"}, [`422 UnprocessableContent`]({{links.mdnStatus}}/422){:target="\_blank"}, [`500 InternalError`]({{links.mdnStatus}}/500){:target="\_blank"}, [`502 BadGateway`]({{links.mdnStatus}}/502){:target="\_blank"} e [`504 GatewayTimeout`]({{links.mdnStatus}}/504){:target="\_blank"}.

**Erros da aplicação** são modelos criados a partir da [classe base `Exception`]({{links.pythonDocs}}/exceptions.html#Exception){:target="\_blank"} que indica que ocorreu um **erro** na parte central da operação/processamento da aplicação. Os implementados são [`InterruptError`]({{links.domain}}/exceptions.py){:target="\_blank"} para o **sinal de interrupção de desligamento/saída** e [`ScopusAPIError`]({{links.domain}}/exceptions.py){:target="\_blank"} para o erro de status {{abbr.http}} da **Scopus Search API**.

**Manipuladores de exceção** são rotinas projetadas para processar e responder rapidamente à ocorrência de **exceções/erros** ou situações especiais específicas durante a execução de um programa, retornando sua representação {{abbr.json}}. Os manipuladores implementados são para [Starlette `HTTPException`](https://www.starlette.io/exceptions/#httpexception){:target="\_blank"}, [FastAPI `HTTPException`]({{links.fastapiTutorial}}/handling-errors/#use-httpexception){:target="\_blank"}, [`RequestValidationError`]({{links.fastapiTutorial}}/handling-errors/#requestvalidationerror-vs-validationerror){:target="\_blank"}, [`ResponseValidationError`]({{links.fastapiTutorial}}/handling-errors/#requestvalidationerror-vs-validationerror){:target="\_blank"}, [`ValidationError`](https://docs.pydantic.dev/latest/errors/validation_errors/){:target="\_blank"}, [`HTTPException`]({{links.exceptions}}/http_exceptions.py){:target="\_blank"}, [`ApplicationError`]({{links.domain}}/exceptions.py){:target="\_blank"} e [`Exception`]({{links.pythonDocs}}/exceptions.html#Exception){:target="\_blank"}.

Sobre a **Resposta** {{abbr.json}} **de Exceção**:

| **Campo**   | **Tipo**        | **Descrição**                                                                       |
| ----------- | --------------- | ----------------------------------------------------------------------------------- |
| `success`   | `bool`          | Resultado da operação, que é um fracasso já que é uma exceção. **Deafult:** `False` |
| `code`      | `int`           | Código de status de erro {{abbr.http}}                                              |
| `message`   | `str`           | Descrição da exceção/erro                                                           |
| `request`   | `dict[str,Any]` | Contém alguns dados de solicitação em um `dict`                                     |
| `errors`    | `Errors`        | Contém alguns detalhes da exceção/erro em um `dict`. **Deafult:** `None`            |
| `timestamp` | `str`           | O _timestamp_ de data e hora como uma `str` no formato {{abbr.iso}}                 |

Sobre o **campo `request`**:

| **Campo** | **Descrição**                                              |
| --------- | ---------------------------------------------------------- |
| `host`    | O host do cliente da solicitação. **Default:** `127.0.0.1` |
| `port`    | A porta do cliente da solicitação. **Default:** `8000`     |
| `method`  | O method da solicitação                                    |
| `url`     | O caminho da {{abbr.url}} da solicitação                   |
| `headers` | Os cabeçalhos da solicitação                               |

Sobre e os **detalhes do erro `ScopusAPIError`**:

| **Campo**   | **Descrição**                                                                       |
| ----------- | ----------------------------------------------------------------------------------- |
| `status`    | Código de erro de status {{abbr.http}} das **APIs da Scopus**                       |
| `api_error` | Descrição do erro de status da resposta das **APIs da Scopus**. **Deafult:** `null` |
| `content`   | O próprio conteúdo da resposta {{abbr.json}} das **APIs da Scopus**                 |

!!! note

    Veja a descrição do erro de status das respostas na [documentação]({{links.scSearchApi}}){:target="\_blank"}.

<br>
<!-- Middlewares -->

## Middlewares

**Middlewares** são mecanismos criados a partir do [Starlette `BaseHTTPMiddleware`](https://www.starlette.io/middleware/#basehttpmiddleware){:target="\_blank"} que funcionam no **ciclo de solicitação-resposta** da aplicação, interceptando chamadas e processando-as. Eles podem acessar e manipular cada **objeto de solicitação** antes que ele seja processado por qualquer manipulador de rota, e também cada **objeto de resposta** antes de retorná-lo. Há três implementados.

O _middleware_ [`TraceExceptionControl`]({{links.middleware}}/tracing_exception.py){:target="\_blank"} **rastreia** a solicitação, relatando o cliente, a {{abbr.url}} acessada, o código de status da resposta e o tempo de processamento. Ele também **lida** com quaisquer exceções inesperadas e erros de interrupção de sinal.

O _middleware_ [`RedirectNotFoundRoutes`]({{links.middleware}}/redirect_route.py){:target="\_blank"} **redireciona** qualquer solicitação de rota não encontrada que receba um erro [`404 Not Found`]({{links.mdnStatus}}/404){:target="\_blank"} e não seja uma rota permitida mapeada. Ele também **lida** com erros de interrupção de sinal.

O _middleware_ [FastAPI `CORSMiddleware`]({{links.fastapiTutorial}}/cors/#use-corsmiddleware){:target="\_blank"} implementa e configura o [mecanismo {{abbr.cors}}](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS){:target="\_blank"}, permitindo qualquer origem, quaisquer credenciais, qualquer cabeçalho e apenas o [método `GET`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET){:target="\_blank"}.

<br>
<!-- SignalHandler -->

## <code class="badge-class"></code> <span class="code-class">SignalHandler</span>

:material-text-box: Defina os manipuladores de sinal para definir o sinalizador do **evento de desligamento**<br>
:material-github: [`código fonte`]({{links.utils}}/signal_handler.py){:target="\_blank"}
:material-package-variant-closed: `utils`<br>
:material-file-code: `app/utils/signal_handler.py`<br>

```py
class SignalHandler(
    for_async: bool = None
)
```

Crie um objeto de **evento**, seja um [threading `Event`]({{links.pythonDocs}}/threading.html#event-objects){:target="\_blank"} ou [asyncio `Event`]({{links.pythonDocs}}/asyncio-sync.html#asyncio.Event){:target="\_blank"} com base no valor do **parâmetro**, e registre seus manipuladores para os sinais [`SIGINT`]({{links.pythonDocs}}/signal.html#signal.SIGINT){:target="\_blank"} e [`SIGTERM`]({{links.pythonDocs}}/signal.html#signal.SIGTERM){:target="\_blank"} usando a função [`signal()`]({{links.pythonDocs}}/signal.html#signal.signal){:target="\_blank"}. Os manipuladores capturarão **sinais de desligamento** e definirão o **sinalizador de evento**. Então, operações baseadas em **processos** ou **_threads_** podem ser encerradas **graciosamente**.

!!! info

    Um **desligamento gracioso** (*graceful shutdown*) é um processo controlado e ordenado para executar um **desligamento seguro** e liberar recursos quando a aplicação é interrompido repentinamente ou recebe um sinal de desligamento/encerramento.

| **Parâmetro** | **Tipo** | **Descrição**                                                      |
| ------------- | -------- | ------------------------------------------------------------------ |
| `for_async`   | `bool`   | Indica se o **evento** será assíncrono ou não. **Default:** `None` |
