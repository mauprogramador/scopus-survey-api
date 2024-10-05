# Limite das APIs & Campos & Filtragem

## Limite das APIs

Há um limite para quantas solicitações você pode fazer para [{{abbr.api}}s da Scopus]({{links.scApis}}){:target="\_blank"} usando sua `Chave da API`. Após cada solicitação, a {{abbr.api}} retornará algumas informações sobre a disponibilidade de sua `Chave da API` nos [cabeçalhos]({{links.scApiKey}}){:target="\_blank"} da resposta. Esse limite de cota é **redefinido a cada sete dias**.

```json
"X-RateLimit-Limit": "Mostra o limite de cota de solicitações de API",
"X-RateLimit-Remaining": "Mostra a cota restante de solicitação da API",
"X-RateLimit-Reset": "Data/hora em segundos *Epoch* de quando a cota da API será redefinida"
```

!!! info

    [Epoch](https://en.wikipedia.org/wiki/Epoch_(computing)){:target="\_blank"} é o número de segundos decorridos desde 1º de janeiro de 1970, também conhecido como [horário Unix](https://en.wikipedia.org/wiki/Unix_time){:target="\_blank"}.

## Cota Excedida

Se a **cota de solicitações** ou a **taxa** {{abbr.throttling}} da {{abbr.api}} for excedida, você receberá um erro de status {{abbr.http}} [429: Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429){:target="\_blank"}.

```json
"X-ELS-Status": "QUOTA_EXCEEDED - Quota Exceeded"
```

!!! note

    Saiba mais sobre a [cota de quantos dados uma `Chave da API` pode recuperar]({{links.scApiKey}}){:target="\_blank"}.

## Mapeamento de Campos

Levando em conta que o objetivo desta aplicação é realizar um levantamento de referenciais teóricos para pesquisa e embasamento de futuros trabalhos acadêmicos, selecionamos um **conjunto** de **informações específicas** dos **metadados dos artigos**.

| **Campo**                 | **Coluna**               | **Descrição**                                        |
| ------------------------- | ------------------------ | ---------------------------------------------------- |
| `link ref=scopus`         | Article Preview Page URL | URL da página de visualização do artigo do Scopus    |
| `dc:identifier`           | Scopus ID                | ID Scopus do Artigo                                  |
| `authors` or `dc:creator` | Authors                  | Lista completa de autores ou apenas o primeiro autor |
| `dc:title`                | Title                    | Título do artigo                                     |
| `prism:publicationName`   | Publication Name         | Título da fonte                                      |
| `dc:description`          | Abstract                 | Resumo completo do artigo                            |
| `prism:coverDate`         | Date                     | Data de publicação                                   |
| `eid`                     | Electronic ID            | ID Electrônico do Artigo                             |
| `prism:doi`               | DOI                      | Identificador de Objeto do Documento                 |
| `prism:volume`            | Volume                   | Identificador para uma publicação em série           |
| `citedby-count`           | Citations                | Contagem de citações                                 |

!!! note

    Veja um exemplo de uma [página de visualização de um artigo da Scopus](https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=0037368024&origin=inward){:target="\_blank"}.

## Filtrando Resultados

Para fornecer maior consistência, todos os dados passam por três etapas de filtragem:

**1.** Primeiramente, todas as **repetições exatas** serão removidas.<br>

**2.** Em Segundo lugar, todos os resultados com exatos **mesmo título** e **mesmos autores** serão removidos.<br>

**3.** Finalmente, todos os resultados com **títulos similares** e provenientes dos **mesmos autores** serão removidos.

Para realizar o terceiro passo, nós iremos [selecionar](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html){:target="\_blank"} dois ou mais artigos que tenham exatamente os **mesmos autores**. Depois disso, usaremos a biblioteca [TheFuzz](https://github.com/seatgeek/thefuzz){:target="\_blank"}, que usa a [Distância de Levenshtein](https://en.wikipedia.org/wiki/Levenshtein_distance){:target="\_blank"}, para calcular a **similaridade entre os títulos** dos artigos desses autores repetidos e, por fim, removeremos os artigos cujos títulos sejam **pelo menos `80%` semelhantes**.

Artigos que não tenham **autores repetidos** ou **títulos semelhantes** serão desconsiderados. Uma mensagem de **log** será exibida indicando a porcentagem de perda total dos artigos.
