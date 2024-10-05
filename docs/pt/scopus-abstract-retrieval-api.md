# Scopus Abstract Retrieval API

Após obter os **IDs Scopus** dos artigos, o próximo passo é usá-los para recuperar todas as informações sobre cada artigo. Usaremos a [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}, fornecida pela [Elsevier]({{links.elsevier}}){:target="\_blank"}, para recuperar os **resumos Scopus** com **ricos metadados de artigos** de todos os artigos.

!!! info

    Na versão antiga `v2.0.0`, fazíamos web scraping da [página de visualização do artigo da Scopus](https://www.scopus.com/home.uri?zone=header&origin=recordpage){:target="\_blank"} usando o [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/){:target="\_blank"}, mas agora abandonamos essa prática.

## URL do Recurso da API

Precisamos solicitar a {{abbr.url}} abaixo e passar alguns parâmetros para obter o **resumo Scopus**.

```url
https://api.elsevier.com/content/abstract/scopus_id
```

## ID Scopus

Para recuperar um **resumo Scopus** de um artigo específico, precisamos definir o *path parameter* `scopus_id`, que se refere a um **identificador Scopus exclusivo** atribuído a cada **artigo/resumo Scopus**.

```text
/{scopus_id}
```

:material-information: Exemplo com **SCOPUS_ID:85197125619** como **ID Scopus**:

```text
/SCOPUS_ID:85197125619
```

## Campos

Ao especificar os [Campos Scopus](https://dev.elsevier.com/sc_abstract_retrieval_views.html){:target="\_blank"}, nós podemos filtrar a resposta e obter apenas as informações desejadas dos artigos.

```text
field=field1,field2,field3,...
```

:material-information: Exemplo com todos os **campos** usados:

```text
field=dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors
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
"X-ELS-APIKey": "Sua Chave da API"
```

## URL Final

Este é um exemplo de uma {{abbr.url}} completa com todos os parâmetros que solicitamos.

```url
https://api.elsevier.com/content/abstract/scopus_id/SCOPUS_ID:85197125619&field=dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors
```

## Corpo da Resposta

Exemplo de um corpo de resposta da **Scopus Abstract Retrieval API** em uma **rede institucional**.

```json
"abstracts-retrieval-response": {
    "coredata": {
        "eid": "2-s2.0-85197125619",
        "citedby-count": "0",
        "prism:volume": "14",
        "dc:description": "The advancement of technology has significantly transformed the livestock [...]",
        "prism:coverDate": "2024-06-01",
        "dc:title": "Digital and Precision Technologies in Dairy Cattle Farming: A Bibliometric Analysis",
        "dc:creator": {
            "author": [
                {
                    "ce:given-name": "Franck Morais",
                    "preferred-name": {
                        "ce:given-name": "Franck Morais",
                        "ce:initials": "F.M.",
                        "ce:surname": "de Oliveira",
                        "ce:indexed-name": "de Oliveira F.M."
                    },
                    "@seq": "1",
                    "ce:initials": "F.M.",
                    "@_fa": "true",
                    "affiliation": {
                        "@id": "60017841",
                        "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                    },
                    "ce:surname": "de Oliveira",
                    "@auid": "57275191700",
                    "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                    "ce:indexed-name": "de Oliveira F.M."
                }
            ]
        },
        "prism:doi": "10.3390/ani14121832",
        "publishercopyright": "© 2024 by the authors.",
        "prism:publicationName": "Animals",
        "dc:identifier": "SCOPUS_ID:85197125619"
    },
    "authors": {
        "author": [
            {
                "ce:given-name": "Franck Morais",
                "preferred-name": {
                    "ce:given-name": "Franck Morais",
                    "ce:initials": "F.M.",
                    "ce:surname": "de Oliveira",
                    "ce:indexed-name": "de Oliveira F.M."
                },
                "@seq": "1",
                "ce:initials": "F.M.",
                "@_fa": "true",
                "affiliation": {
                    "@id": "60017841",
                    "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                },
                "ce:surname": "de Oliveira",
                "@auid": "57275191700",
                "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                "ce:indexed-name": "de Oliveira F.M."
            }
        ]
    }
}
```

| **Campo**                      | **Descrição**                                                       |
| ------------------------------ | ------------------------------------------------------------------- |
| `abstracts-retrieval-response` | Lista os ricos metadados do artigo                                  |
| `coredata`                     | Lista os principais metadados do artigo com os campos especificados |
| `authors`                      | Lista todos os autores do artigo                                    |
| `author`                       | Lista os dados de todos os autores do artigo                        |

Exemplo de um corpo de resposta da **Scopus Abstract Retrieval API** em uma **rede fora do campus**.

```json
"abstracts-retrieval-response": {
    "coredata": {
        "eid": "2-s2.0-85197125619",
        "citedby-count": "0",
        "prism:volume": "14",
        "prism:coverDate": "2024-06-01",
        "dc:title": "Digital and Precision Technologies in Dairy Cattle Farming: A Bibliometric Analysis",
        "dc:creator": {
            "author": [
                {
                    "ce:given-name": "Franck Morais",
                    "preferred-name": {
                        "ce:given-name": "Franck Morais",
                        "ce:initials": "F.M.",
                        "ce:surname": "de Oliveira",
                        "ce:indexed-name": "de Oliveira F.M."
                    },
                    "@seq": "1",
                    "ce:initials": "F.M.",
                    "@_fa": "true",
                    "affiliation": {
                        "@id": "60017841",
                        "@href": "https://api.elsevier.com/content/affiliation/affiliation_id/60017841"
                    },
                    "ce:surname": "de Oliveira",
                    "@auid": "57275191700",
                    "author-url": "https://api.elsevier.com/content/author/author_id/57275191700",
                    "ce:indexed-name": "de Oliveira F.M."
                }
            ]
        },
        "prism:doi": "10.3390/ani14121832",
        "publishercopyright": "© 2024 by the authors.",
        "prism:publicationName": "Animals",
        "dc:identifier": "SCOPUS_ID:85197125619"
    }
}
```

| **Campo**                      | **Descrição**                                                       |
| ------------------------------ | ------------------------------------------------------------------- |
| `abstracts-retrieval-response` | Lista os ricos metadados do artigo                                  |
| `coredata`                     | Lista os principais metadados do artigo com os campos especificados |
| `author`                       | Lista os dados do primeiro autor do artigo                          |
