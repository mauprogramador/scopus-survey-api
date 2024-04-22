# Scopus Search API

Para pesquisar os artigos e recuperar deles as informações que precisamos, estamos utilizando a [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}, que é uma das APIs disponibilizadas pela [Elsevier](https://www.elsevier.com/){:target="\_blank"}. É uma interface de pesquisa associada ao cluster da Scopus, que contém resumos da Scopus.

Para utilizar a **API** precisamos fazer uma requisição URL da **API** e passar alguns parâmetros. Abaixo estão alguns detalhes:

## URL base

A URL base da Scopus Search API

```text
https://api.elsevier.com/content/search/scopus
```

## Consulta

Como nossa busca é baseada em palavras-chave, estamos utilizando um parâmetro de consulta com [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="\_blank"} para especificar nosso método de busca, que é `TITLE-ABS-KEY`, um campo combinado que buscará palavras-chave em resumos, palavras-chave e títulos de artigos.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

Exemplo com **Python** e **Machine Learning** como `Palavras-chave`:

```text
query=TITLE-ABS-KEY(Python+AND+Machine+Learning)
```

## Campos

Para retornar apenas as informações que nos interessam dos artigos, podemos especificar alguns [Scopus Fields](https://dev.elsevier.com/sc_search_views.html){:target="\_blank"} para filtrar a resposta.

```text
field=field1,field2,field3,...
```

Exemplo com todos os **campos** usados:

```text
field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier
```

## Data

O intervalo de datas de interesse para artigos publicados.

```text
date=year1-year2
```

Exemplo com **intervalo de datas** utilizado, é definido automaticamente para os **últimos três anos**:

```text
date=2021-2024
```

## Cabeçalhos da Requisição

Os cabeçalhos básicos que devemos incluir na solicitação. Lembre-se de inserir sua `Api Key`.

```json
"X-ELS-APIKey": "Sua Api Key",
"User-Agent": "Mozilla/5.0",
"Accept": "application/json",
"Content-Type": "application/json"
```

## URL

Este é um exemplo de URL completa com todos os parâmetros que solicitamos.

```text
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python+AND+Machine+Learning)&field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier&date=2021-2024&suppressNavLinks=true
```

O parâmetro **supressNavLinks** é usado para suprimir a inclusão de links de navegação de nível superior no *payload* da resposta.

## Cabeçalhos da Resposta

Após a conclusão da pesquisa, a **API** retornará algumas informações sobre a disponibilidade de uso de sua `Api Key` nos [Cabeçalhos](https://dev.elsevier.com/api_key_settings.html){:target="\_blank"} de resposta, portanto, verifique-a com atenção, principalmente se você usa a **API** gratuitamente como parte de uma instituição de ensino.

```json
"X-RateLimit-Limit": "Mostra o limite de cota de solicitações de API",
"X-RateLimit-Remaining": "Mostra a cota restante da API",
"X-RateLimit-Reset": "Data/hora em segundos da época de quando a cota da API será redefinida"
```

## Corpo da Resposta

O campo `search-results` informa alguns parâmetros dos resultados da busca, como o total de resultados (`totalResults`) e os termos buscados (`Query`). O campo `entry` lista os resultados dos campos dos artigos.

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
                "dc:identifier": "SCOPUS_ID:85137995729",
                "dc:title": "Real Time Facial Emotions Detection of Multiple Faces Using Deep Learning",
                "prism:publicationName": "Lecture Notes in Networks and Systems",
                "prism:volume": "475",
                "prism:coverDate": "2023-01-01",
                "prism:doi": "10.1007/978-981-19-2840-6_29",
                "citedby-count": "0"
            }
        ]
    }
}
```

## Reduzindo a Contagem

Se você quiser, você pode reduzir o número de artigos que serão retornados indo em `app/gateway/api_config.py` e adicionando o parâmetro **count** no atributo **API_URL** da classe **ApiConfig**, que é um valor numérico que representa o número máximo de resultados a ser retornado para a busca.

```py title="api_config.py" linenums="1" hl_lines="5"
class ApiConfig:
    API_URL = (
        'https://api.elsevier.com/content/search/scopus'
        '?query=TITLE-ABS-KEY({query})&field={fields}&date={date}'
        '&suppressNavLinks=true&count=14'
    )
```
