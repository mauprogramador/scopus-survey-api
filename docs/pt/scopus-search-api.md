# Scopus Search API

Usaremos a [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"}, fornecida pela [Elsevier]({{links.elsevier}}){:target="\_blank"}, para pesquisar artigos usando as `Keywords` e obter seus **IDs Scopus**. É uma interface de pesquisa associada ao cluster **Scopus** contendo **resumos Scopus**.

!!! info

    Um [Cluster](https://en.wikipedia.org/wiki/Computer_cluster){:target="\_blank"} é um grupo de servidores/computadores que agem como um único sistema.

## URL do Recurso da API

Precisamos solicitar a {{abbr.url}} abaixo e passar alguns parâmetros para a busca.

```url
https://api.elsevier.com/content/search/scopus
```

## Consulta

Como nossa busca é baseada em `Palavras-chave`, nós estamos utilizando um parâmetro de consulta com [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="\_blank"} para especificar nosso método de busca, que é `TITLE-ABS-KEY`, um campo combinado que buscará as `Palavras-chave` nos resumos, palavras-chave e títulos dos artigos.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

:material-information: Exemplo com **Python** e **Machine Learning** como `Palavras-chave`:

```text
query=TITLE-ABS-KEY(Python+AND+Machine+Learning)
```

## Campos

Ao especificar os [Campos Scopus](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"}, nós podemos filtrar a resposta e obter apenas os **IDs Scopus** dos artigos.

```text
field=field1,field2,field3,...
```

:material-information: Exemplo com o **campo** usado:

```text
field=dc:identifier
```

## Intervalo de Datas

O **intervalo de datas** de interesse para artigos publicados.

```text
date=year1-year2
```

:material-information: Exemplo com o **intervalo de datas** utilizado, é definido automaticamente para os **últimos três anos**:

```text
date=2021-2024
```

## Cabeçalhos da Requisição

Os cabeçalhos incluídos na requisição. Um deles especifica sua `Chave da API`.

```json
"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
"Accept-Encoding": "gzip, deflate, br",
"Referer": "https://www.scopus.com/",
"Origin": "https://www.scopus.com",
"Content-Type": "application/json",
"Accept": "application/json",
"User-Agent": "Mozilla/5.0",
"Connection": "keep-alive",
"X-ELS-APIKey": "Sua Chave da  API"
```

## URL Final

Este é um exemplo de uma {{abbr.url}} completa com todos os parâmetros que solicitamos.

```url
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python+AND+Machine+Learning)&field=dc:identifier&date=2021-2024&suppressNavLinks=true
```

O parâmetro `supressNavLinks` é usado para suprimir a inclusão de links de navegação de nível superior no _payload_ da resposta.

## Corpo da Resposta

Exemplo de um corpo de resposta da **Scopus Search API**.

```json
{
  "search-results": {
    "opensearch:totalResults": "1",
    "opensearch:startIndex": "0",
    "opensearch:itemsPerPage": "1",
    "opensearch:Query": {
      "@role": "request",
      "@searchTerms": "TITLE-ABS-KEY(Images, Machine Learning, Artificial Intelligence, Computer Vision)",
      "@startPage": "0"
    },
    "entry": [
      {
        "@_fa": "true",
        "prism:url": "https://api.elsevier.com/content/abstract/scopus_id/85137995729",
        "dc:identifier": "SCOPUS_ID:85137995729"
      }
    ]
  }
}
```

| **Campo**                 | **Descrição**                                                           |
| ------------------------- | ----------------------------------------------------------------------- |
| `search-results`          | Informa alguns metadados da operação de busca e dos artigos encontrados |
| `opensearch:totalResults` | Número total de artigos encontrados                                     |
| `opensearch:startIndex`   | Índice da paginação da qual começamos a recuperar um grupo de artigos   |
| `opensearch:itemsPerPage` | Número de artigos divididos em cada página, quando há muitos resultados |
| `opensearch:Query`        | Alguns metadados sobre as consultas de busca booleanas enviadas         |
| `entry`                   | Lista de artigos com os campos especificados na busca                   |
