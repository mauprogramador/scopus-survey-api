
# Scopus Search API

Para pesquisar os artigos e recuperar deles as informações que precisamos, estamos utilizando a [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"}, que é uma das APIs disponibilizadas pela [Elsevier](https://www.elsevier.com/){:target="_blank"}. É uma interface de pesquisa associada ao cluster da Scopus, que contém resumos da Scopus.

Para utilizar a API precisamos fazer uma requisição à url da API e passar alguns parâmetros. Abaixo estão alguns detalhes:

## Url base

O URL base da Scopus Search API

```text
https://api.elsevier.com/content/search/scopus
```

## Consulta

Como nossa busca é baseada em palavras-chave, estamos utilizando um parâmetro de consulta com [Scopus Search Tip](https://dev.elsevier.com/sc_search_tips.html){:target="_blank"} para especificar nosso método de busca, que é `TITLE-ABS-KEY`, um campo combinado que buscará palavras-chave em resumos, palavras-chave e títulos de artigos.

```text
query=TITLE-ABS-KEY(keyword1 AND keyword2 AND ...)
```

## Campos

Para retornar apenas as informações que nos interessam dos artigos, podemos especificar alguns [Scopus Fields](https://dev.elsevier.com/sc_search_views.html){:target="_blank"} para filtrar a resposta.

```text
field=field1,field2,field3,...
```

## Data

O intervalo de datas de interesse para artigos publicados.

```text
date=year1-year2
```

## Cabeçalhos da Requisição

Os cabeçalhos básicos que devemos incluir na solicitação. Lembre-se de inserir sua `Api Key`.

```json
"X-ELS-APIKey": "Your Api Key",
"User-Agent": "Mozilla/5.0",
"Accept": "application/json",
"Content-Type": "application/json"
```

## Url

Este é um exemplo de url completa com todos os parâmetros que solicitamos.

```text
https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(Python AND Machine Learning)&field=prism:coverDate,prism:url,prism:publicationName,citedby-count,prism:volume,dc:title,prism:doi,dc:identifier&date=2018-2024&suppressNavLinks=true
```

## Cabeçalhos da Resposta

Após a conclusão da pesquisa, a API retornará algumas informações sobre a disponibilidade de uso de sua `Api Key` nos [Cabeçalhos](https://dev.elsevier.com/api_key_settings.html){:target="_blank"} de resposta, portanto, verifique-a com atenção, principalmente se você usa a API gratuitamente como parte de uma instituição de ensino.

```json
"X-RateLimit-Limit": "Shows API quota setting",
"X-RateLimit-Remaining": "Shows API remaining quota",
"X-RateLimit-Reset": "Date/Time in Epoch seconds when API quota resets"
```
