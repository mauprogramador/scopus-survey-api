# Scopus Searcher API

Instituto Federal de Mato Grosso do Sul ([IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas){:target="\_blank"}) <br/>
Tecnologia em Análise de Desenvolvimento de Sistemas ([TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas){:target="\_blank"}) <br/>
Brasil - MS - Três Lagoas - 26 de Fevereiro de 2024<br/>

**API para Levantamento Bibliográfico de Artigos da Scopus** <br/>

**Código Fonte:** <https://github.com/mauprogramador/scopus-searcher-api>{:target="\_blank"}

---

## Visão geral

Esta **API** foi desenvolvida para facilitar a busca de artigos para pesquisa e desenvolvimento de referenciais teóricos para artigos e trabalhos finais. Ele usará a [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}, mantida pela empresa [Elsevier](https://www.elsevier.com/pt-br){:target="\_blank"}, para permitir pesquisas no cluster da [Scopus](https://www.scopus.com/home.uri){:target="\_blank"}, que é o maior banco de dados de resumos e citações de literatura e fontes de pesquisa de qualidade na web.

Para realizar a busca, você precisará ter o [Python3](https://www.python.org/){:target="\_blank"} ou [Docker](https://www.docker.com/){:target="\_blank"} instalado para executar a aplicação, também será necessário gerar uma `Api Key` e selecionar no máximo quatro `Palavras-chave` com base no tema da sua busca. Inicie o aplicativo, acesse a página web ou [Swagger](https://github.com/swagger-api/swagger-ui){:target="\_blank"}, e envie a `Api Key` e suas `Palavras-chave`, caso algum artigo seja encontrado com sucesso, ele retornará um [arquivo CSV](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="\_blank"} contendo todas as informações.
