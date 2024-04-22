# Levantamento de Dados

Levando em consideração que o objetivo desta aplicação é realizar um levantamento de referenciais teóricos para pesquisas e servir de base para futuros trabalhos acadêmicos, selecionamos um conjunto de informações específicas que serão consolidadas a partir da busca e raspagem dos resultados para referenciar os artigos.

Abaixo segue o mapeamento dos campos de informações:

| Campo                 | Coluna             | Descrição                                       |
| :-------------------- | :----------------- | :---------------------------------------------- |
| prism:publicationName | Nome da Publicação | Título da Fonte                                 |
| prism:coverDate       | Data               | Data de publicação                              |
| dc:identifier         | Scopus ID          | Scopus ID                                       |
| prism:url             | URL                | URI da API de recuperação de resumo de conteúdo |
| dc:title              | Título             | Título do Artigo                                |
| prism:volume          | Volume             | Volume                                          |
| prism:doi             | DOI                | Identificador de objeto de documento            |
| citedby-count         | Citações           | Contagem de citações                            |
| -                     | Autores            | Lista completa de Autores                       |
| -                     | Resumo             | Resumo completo                                 |

Exceto os campos `Autores` e `Resumo` que foram inseridos posteriormente e preenchidos com os resultados da raspagem, todos os outros campos vieram dos resultados de pesquisa da [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}.

## Filtragem

Em ordem de dar maior consistência, todos os dados passaram por três etapas de filtragem:

- Primeiramente, serão removidas todas as **repetições exatas**.
- Em Segundo lugar, serão removidos todos os resultados com exatos **mesmo título** e **mesmos autores**.
- Finalmente, serão removidos todos os resultados com **títulos similares** e provenientes dos **mesmos autores**.

Para realizar o terceiro passo, nós iremos [agrupar](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html){:target="\_blank"} os artigos com base na **coluna dos autores**, de modo que se houver dois ou mais artigos com os exatos mesmos autores eles serão agrupados juntos. Após isso, nós vamos utilizar a biblioteca [FuzzyWuzzy](https://pypi.org/project/fuzzywuzzy/){:target="\_blank"}, que usa a [Distância Levenshtein](https://en.wikipedia.org/wiki/Levenshtein_distance){:target="\_blank"}, para calcular a diferênça entre os títulos, removendo os artigos cujos cujos títulos forem pelo menos `80%` similares.

!!! note

    Caso o último passo for processado, será exibido uma mensagem indicando a porcetagem da perda total de artigos.
