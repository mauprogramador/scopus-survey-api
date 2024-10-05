# Scopus Searcher API

<figure markdown="span">
  ![Logo](../assets/img/logo.png "Scopus Searcher API Logo"){ width="300" }
  <figcaption>API Web para Levantamento Bibliográfico de Artigos da Scopus</figcaption>
</figure>
<p align="center">
  <a href="{{links.workflows}}/verification.yml" target="_blank" title="Linting and Testing Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/verification.yml?branch=master&event=push&logo=github&label=Lint | Test&color=FF5722" alt="Linting and Testing Action">
  </a>
  <a href="{{links.workflows}}/documentation.yml" target="_blank" title="Documentation Action">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-searcher-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=2196F3" alt="Documentation Action">
  </a>
  <img src="https://img.shields.io/badge/Coverage-99%25-4CAF50" alt="Coverage" title="Coverage">
  <a href="{{links.releases}}/v2.0.0" target="_blank" title="API Version">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-searcher-api?logo=github&label=API Version&color=E9711C" alt="API Version">
  </a>
  <a href="https://www.python.org/" target="_blank" title="Python3 Version">
    <img src="https://img.shields.io/badge/Python-v3.11-3776AB?logo=python&logoColor=FFF" alt="Python3 Version">
  </a>
</p>

---

Instituto Federal de Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas){:target="\_blank"} <br/>
Tecnologia em Análise de Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas){:target="\_blank"} <br/>
Brasil - MS - Três Lagoas <br/>

**Código Fonte:** <{{links.repository}}>{:target="\_blank"}

---

## Visão geral

Esta aplicação foi desenvolvida para facilitar a busca de artigos para pesquisa e desenvolvimento de referenciais teóricos. Ela usará ambos a [Scopus Search API]({{links.scSearchApi}}){:target="\_blank"} e a [Scopus Abstract Retrieval API]({{links.scAbstractRetrievalApi}}){:target="\_blank"}, mantidas pela empresa [Elsevier]({{links.elsevier}}){:target="\_blank"}, para consultar o cluster da [Scopus](https://www.scopus.com/home.uri){:target="\_blank"}, que é o maior banco de dados de resumos e citações de literatura e fontes de pesquisa de qualidade na web.

Para realizar a busca, você precisará ter o [Python3](https://www.python.org/){:target="\_blank"} ou [Docker](https://www.docker.com/){:target="\_blank"} instalado para executar a aplicação, você também precisará gerar uma `Chave da API` e **selecionar no máximo quatro** `Palavras-chave` com base no tema da sua pesquisa. Inicie a aplicação, vá para a página web, submeta sua `Chave da API` e suas `Palavras-chave`, e, caso algum artigo for encontrado, um arquivo {{abbr.csv}} contendo todas as informações dos artigos será retornado.

!!! note

    Este projeto está licenciado sob os termos da [licença MIT](./license.md).
