# Levantamento de Dados

Levando em consideração que o objetivo desta aplicação é realizar um levantamento de referenciais teóricos para pesquisas e servir de base para futuros trabalhos acadêmicos, selecionamos um conjunto de informações específicas que serão consolidadas a partir da busca e raspagem dos resultados para referenciar os artigos.

Abaixo segue o mapeamento dos campos de informações:

| Campo                 | Coluna             | Descrição                                       |
| :-------------------- | :----------------- | :---------------------------------------------- |
| prism:publicationName | Nome da Publicação | Título da Fonte                                 |
| prism:coverDate       | Data               | Data de publicação                              |
| dc:identifier         | Scopus ID          | -                                               |
| prism:url             | URL                | URI da API de recuperação de resumo de conteúdo |
| dc:title              | Título             | Título do Artigo                                |
| prism:volume          | Volume             | -                                               |
| prism:doi             | DOI                | Identificador de objeto de documento            |
| citedby-count         | Citações           | Contagem de citações                            |
| -                     | Autores            | Lista completa de Autores                       |
| -                     | Resumo             | Resumo completo                                 |

Exceto os campos `Autores` e `Resumo` que foram inseridos posteriormente e preenchidos com os resultados da raspagem, todos os outros campos vieram dos resultados de pesquisa da [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"}. Os dados serão filtrados, primeiro removendo repetições exatas e depois removendo resultados com o mesmo título e mesmos autores.
