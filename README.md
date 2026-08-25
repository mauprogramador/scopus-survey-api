# Scopus Survey API

<p align="center">
  <img src="./docs/assets/img/logo.png" width="250" alt="Logo">
  <img src="./web/static/img/ifms.ico" width="16" alt="IFMS">
  <img src="./web/static/img/scopus.ico" width="16" alt="Scopus">
</p>
<p align="center">
  <em>API da Web para levantamento bibliográfico de artigos da Scopus</em>
</p>
<p align="center">
  <a href="https://github.com/mauprogramador/scopus-survey-api/actions/workflows/verification.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-survey-api/verification.yml?branch=master&event=push&logo=github&label=Lint%26Teste&color=C5362B" alt="Lint & Teste">
  </a>
  <a href="https://github.com/mauprogramador/scopus-survey-api/actions/workflows/documentation.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/mauprogramador/scopus-survey-api/documentation.yml?branch=master&event=push&logo=github&label=Docs&color=2196F3" alt="Documentation">
  </a>
  <img src="https://img.shields.io/badge/Cobertura-99%25-4CAF50" alt="Cobertura">
  <a href="https://github.com/mauprogramador/scopus-survey-api/releases/latest">
    <img src="https://img.shields.io/github/v/tag/mauprogramador/scopus-survey-api?logo=github&label=Versão&color=E9711C" alt="Última Versão">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-v3.12-FBDA4E?logo=python&logoColor=FFF&labelColor=3776AB" alt="Versão do Python3">
  </a>
</p>
<p align="center">
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=FFF" alt="FastAPI">
  </a>
  <a href="https://docs.pydantic.dev/latest/">
    <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=FFF" alt="Pydantic">
  </a>
  <a href="https://pandas.pydata.org/docs/">
    <img src="https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=FFF" alt="Pandas">
  </a>
  <a href="https://docs.aiohttp.org/en/stable/">
    <img src="https://img.shields.io/badge/AIOHTTP-2C5BB4?logo=aiohttp&logoColor=FFF" alt="AIOHTTP">
  </a>
  <a href="https://getbootstrap.com/docs/5.3/getting-started/introduction/">
    <img src="https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=FFF" alt="Bootstrap">
  </a>
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/Poetry-60A5FA?logo=poetry&logoColor=FFF" alt="Poetry">
  </a>
  <a href="https://docs.pytest.org/en/stable/">
    <img src="https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=FFF" alt="Pytest">
  </a>
  <a href="https://www.mkdocs.org/">
    <img src="https://img.shields.io/badge/MkDocs-526CFE?logo=materialformkdocs&logoColor=FFF" alt="MkDocs">
  </a>
</p>
<p align="center">
  <a href="https://black.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/estilo_de_código-black-000" alt="Black">
  </a>
  <a href="https://mypy.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/mypy-verificado-2A6DB2" alt="MyPy">
  </a>
  <a href="https://pylint.readthedocs.io/en/stable/">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" alt="Pylint">
  </a>
  <a href="https://bandit.readthedocs.io/en/latest/">
    <img src="https://img.shields.io/badge/segurança-bandit-yellow" alt="Bandit">
  </a>
  <a href="https://bandit.readthedocs.io/en/latest/">
    <img src="https://img.shields.io/badge/auditoria-pip audit-3775A9" alt="Pip-Audit">
  </a>
</p>

---

> **Note:** This repository is documented in **Portuguese (Brazil)** for academic and accessibility purposes.<br>
> 🌐 **Read in** [**English [`en-US`]**](README.en.md).

<br>

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul &nbsp;&#8226;&nbsp; [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Tecnologia em Análise e Desenvolvimento de Sistemas &nbsp;&#8226;&nbsp; [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>
Dados fornecidos pela [Scopus](https://www.scopus.com)® &nbsp;&#8226;&nbsp; © [Elsevier](https://www.elsevier.com/pt-br)

- Documentação: <https://mauprogramador.github.io/scopus-survey-api/>
- API da Web: <http://127.0.0.1:8000/v2/scopus-survey/en-US/search-articles>
- Swagger UI: <http://127.0.0.1:8000/>

<br>

## 1. Visão Geral

Esta **API web** foi projetada para realizar **levantamentos bibliográficos sistemáticos utilizando dados da [base Scopus](https://www.elsevier.com/pt-br/products/scopus)**, promovendo o acesso a fontes bibliográficas relevantes e de alta qualidade por meio de uma interface simples e bem documentada, reduzindo assim a barreira inicial de entrada de **estudantes** e acadêmicos.

Como uma ferramenta de automação [gratuita e acadêmica](https://dev.elsevier.com/academic_research_scopus.html), a aplicação integra **múltiplos critérios de seleção**, incluindo múltiplos parâmetros de consulta, combinações de palavras-chave e [busca booleana](https://dev.elsevier.com/sc_search_tips.html), com **mecanismos** para recuperação, validação, serialização e filtragem personalizada de **grandes volumes de dados** das [APIs Scopus](https://dev.elsevier.com/sc_apis.html).

Dessa forma, apenas os **dados mais relevantes e recentes** serão mantidos e retornados em um **arquivo CSV**, tornando-os adequados para estudos e levantamentos bibliométricos, pesquisas, [revisões sistemáticas](https://pt.wikipedia.org/wiki/Revis%C3%A3o_sistem%C3%A1tica), etc., permitindo que estudantes reúnam rapidamente um conjunto de fontes de literatura revisadas por pares para uma tese ou projeto.

<br>

## 2. Configuração

Crie um arquivo `.env` para configurar as seguintes opções:

| **Parâmetro**  | **Descrição**                                                                                     | **_Default_** |
| -------------- | ------------------------------------------------------------------------------------------------- | ------------- |
| `SECRET_KEY`   | Usado para assinar (criptografia) os tokens CSRF                                                  |               |
| `HOST`         | Define o endereço do host no qual a aplicação será executada                                      | `127.0.0.1`   |
| `PORT`         | Define a porta do servidor na qual a aplicação será executada                                     | `8000`        |
| `RELOAD`       | Ativa o recarregamento automático, em caso de alterações nos arquivos, para desenvolvimento local | `false`       |
| `WORKERS`      | Define vários processos de trabalho                                                               | `1`           |
| `LOG_LEVEL`    | Define o nível de log                                                                             | `false`       |
| `PROGRESS_BAR` | Exibe a barra de progresso do processo do consumo de dados das APIs                               | `true`        |
| `LOGGING_FILE` | Ativa o salvamento de logs em arquivo                                                             | `false`       |

- As opções `RELOAD` e `WORKERS` são **mutuamente exclusivas**.

- Configurar o `HOST` para `0.0.0.0` torna a aplicação disponível externamente.

> [!NOTE]
> O endereço `0.0.0.0` não é um domínio válido para **Cross-Origin-Opener-Policy**, use `localhost` em vez disso.

- Defina os `WORKERS` para iniciar **múltiplos processos do servidor**. Será definido automaticamente com base no **número de CPUs** se o valor `-1` for usado.

  ```py
  # Workers = (2 * CPU Cores) + 1
  try:
      return (2 * len(os.sched_getaffinity(0))) + 1
  except AttributeError:
      return (2 * (os.cpu_count() or 2)) + 1
  ```

- Níveis de log disponíveis: `DEBUG`, `API_CALL`, `INFO`, `ACCESS`, `QUOTA`, `WARNING`, `ERROR`, e `EXCEPTION`.

- Em produção, `RELOAD` e `PROGRESS_BAR` são desativados automaticamente, e o `LOG_LEVEL` é automaticamente definido para `INFO`.

> [!TIP]
> Dê uma olhada no arquivo [`.env.example`](./.env.example).

<br>

## 3. Execução

### 3.1. Execute com um Ambiente Virtual (venv) do Python

Você precisará do [Python3.12](https://www.python.org/downloads/release/python-31211/) com o [Pip](https://pip.pypa.io/en/stable/installation/) e o [Venv](https://docs.python.org/3/library/venv.html) instalados.

```bash
# Crie um novo ambiente virtal (.venv)
make venv

# Ative o Venv
source .venv/bin/activate
```

### 3.1.1. Execute em Ambiente de Desenvolvimento (Poetry)

Instale o [Poetry](https://python-poetry.org/) com todas as dependências: `app`, `dev`, `tests`, `docs` e execute com o [Uvicorn](https://uvicorn.dev/).

```bash
# Instale todos os grupos de dependencias do pyproject.toml com o Poetry
(.venv) make install-dev

# Execute com o Poetry
(.venv) make run-dev
```

### 3.1.2. Execute em Ambiente de Produção (Pip)

Instale apenas as principais dependências, `app`, e execute com o [Gunicorn](https://gunicorn.org/).

```bash
# Instale apenas as principais dependências do requirements.txt com o Pip
(.venv) make install-prod

# Execute com o Gunicorn
(.venv) make run-prod
```

### 3.2. Execute com o Docker

Você precisará ter o [Docker](https://www.docker.com/) instalado. Crie a imagem `scopus-survey-api` a partir do [Dockerfile](https://docs.docker.com/reference/dockerfile/), instale apenas as principais dependências do `requirements.txt` com o [Pip](https://pip.pypa.io/en/stable/installation/) e execute com o [Uvicorn](https://uvicorn.dev/).

```bash
# Execute em um contêiner Docker a partir do Dockerfile
make docker

# Acompanhe e exiba os últimos logs
make docker-logs
```

<br>

## 4. Informações Importantes

### 4.1. Fonte de Dados

Declaramos que todo o uso do [banco de dados](https://www.elsevier.com/pt-br/products/scopus) [Scopus](https://www.scopus.com)® e suas [APIs](https://dev.elsevier.com/sc_apis.html), de propriedade e mantenabilidade da © [Elsevier B.V.](https://www.elsevier.com/pt-br), destina-se exclusivamente à [pesquisa acadêmica não comercial](https://dev.elsevier.com/academic_research_scopus.html), **sem implicar endosso ou afiliação**, e está sujeito aos [nossos Termos de Serviço](./legal/pt_BR/TERMS_OF_SERVICE.md), bem como aos [Termos da Elsevier](https://www.elsevier.com/pt-br/legal/elsevier-website-terms-and-conditions) e à [Política da Scopus](https://dev.elsevier.com/academic_research_scopus.html). Todos os dados que manipulamos são obtidos **"NO ESTADO EM QUE SE ENCONTRAM"** e, portanto, não garantimos nem assumimos responsabilidade por quaisquer erros ou imprecisões nos mesmos.

> [!CAUTION]
> **É estritamente proibido o uso indevido ou a tentativa de uso indevido de dados obtidos das APIs da Scopus, em violação ao [Contrato de Serviço de API da Elsevier](https://dev.elsevier.com/policy/API-service-agreement.pdf).**

### 4.2. Manipulação de Dados

Em geral, os dados serão preservados sem qualquer alteração direta, necessitando apenas de serem devidamente validados com base nos campos de resposta das APIs:

- Aqueles que retornaram algum valor serão mantidos como estão;
- Aqueles que não retornaram valor algum serão definidos como "`None`" (ou "") por padão;
- O campo "`autores`" será definido como o primeiro autor ("`dc:creator`") ou todos os autores ("`authors`") concatenados, dependendo do que for retornado.

Por fim, os documentos serão **filtrados e removidos** na seguinte ordem:

1. Duplicatas exatas, sendo mantido o primeiro.
2. Documentos com mesmo título e mesmo(s) autor(es), sendo mantido o primeiro.
3. Documentos do mesmo(s) autor(es) com títulos semelhantes, sendo mantido o documento com a data de publicação mais recente.

### 4.3. Busca

Utilizamos o [campo combinado "`TITLE-ABS-KEY`"](https://dev.elsevier.com/sc_search_tips.html) para **buscar simultaneamente combinações de palavras-chave nos resumos, palavras-chave e títulos, e recuperar os documentos onde elas são encontradas**. Também utilizamos os campos "`date`" e "`sort`" para delimitar o período de interesse das publicações, e ordenar por ano e data de publicação e por relevância, além de outros campos **adicionais opcionais** na busca para produzir resultados mais relevantes.

Em relação ao fluxo da pesquisa, primeiro recuperamos o número total de resultados encontrados para cada combinação de palavras-chave, depois realizamos a pesquisa final com a combinação selecionada para obter o **Scopus ID** de todos os resultados, recuperando por fim um conjunto de dados abrangente com metadados bibliográficos.

### 4.4. Chave de API

De acordo com o [Contrato de Serviço de API](https://dev.elsevier.com/policy/API-service-agreement.pdf) e as [Políticas de Uso](https://dev.elsevier.com/policy.html), a **Elsevier** emitirá a você uma **Chave de API** que lhe concede uma licença limitada para usar as [APIs da Scopus](https://dev.elsevier.com/sc_apis.html), para que você possa se autenticar adequadamente para consultar o banco de dados Scopus. Ela pode ser obtida acessando o [Portal do Desenvolvedor da Elsevier](https://dev.elsevier.com/) e realizando um cadastro. Se você faz parte de uma **instituição educacional**, pode tentar [fazer login usando o e-mail institucional ou acadêmico da sua organização](https://www.scopus.com/signin.uri).

### 4.5. Rede Institucional

Esteja ciente de que a **Chave de API** só será autenticada corretamente se você a enviar enquanto estiver usando a **rede da sua instituição acadêmica**, que deve estar **registrada na Elsevier**. Isso **não inclui** acesso <abbr title="Rede Privada Virtual">VPN</abbr> ou proxy. Portanto, se você estiver **totalmente remoto** e **fora do campus**, alguns dados poderão **não ser retornados**.

### 4.6. Cota e Taxa de Solicitação (_Rate Limit_)

Há um **limite máximo para o número de solicitações** que podemos fazer às [APIs Scopus](https://dev.elsevier.com/sc_apis.html) usando sua **Chave de API**. Essa **cota de solicitações é redefinida a cada sete dias**, é **exclusiva para cada API** e você pode **verificar sua disponibilidade no painel de detalhes após cada operação**. Se as solicitações **excederem a cota ou a taxa de solicitação**, um **erro será retornado**. Veja as [Configurações da Chave de API](https://dev.elsevier.com/api_key_settings.html).

| API da Scopus          | Cota Semanal | _Rate Limit_ |
| ---------------------- | ------------ | ------------ |
| Search API             | 20,000       | 9req/s       |
| Abstract Retrieval API | 10,000       | 9req/s       |

<br>

## 5. Resultados

### 5.1. Campos Obtidos

Campos mapeados no arquivo CSV

| Campo                     | Coluna                   | Descrição                                      |
| :------------------------ | :----------------------- | :--------------------------------------------- |
| link `ref=scopus`         | Article Preview Page URL | URL da página de visualização do artigo Scopus |
| `dc:identifier`           | Scopus ID                | ID Scopus do Artigo                            |
| `authors` or `dc:creator` | Authors                  | Primeiro autor ou lista completa de autores    |
| `dc:title`                | Title                    | Título do artigo                               |
| `prism:publicationName`   | Publication Name         | Título da fonte / Nome de Publicação           |
| `dc:description`          | Abstract                 | Resumo completo do artigo                      |
| `prism:coverDate`         | Date                     | Data de publicação                             |
| `eid`                     | Electronic ID            | ID Electrônico do Documento                    |
| `prism:doi`               | DOI                      | Identificador de Objeto do Documento           |
| `prism:volume`            | Volume                   | Identificador para uma publicação em série     |
| `citedby-count`           | Citations                | Número de citações                             |

### 5.2. Metadados do CSV

Como o resultado do levantamento é um arquivo CSV, que é essencialmente um conjunto de dados obtido das APIs Scopus, devemos [**reconhecer** tanto o Scopus quanto a Elsevier como **fontes de dados**](https://dev.elsevier.com/tecdoc_attribution_scopus.html). Portanto, adicionaremos alguns metadados no **início do arquivo (4 linhas) como comentários** indicando os parâmetros utilizados, detalhes do levantamento e a data em que os dados foram obtidos.

**Exemplo:**

```txt
# GeneratedBy: ScopusSurveyAPI https://github.com/mauprogramador/scopus-survey-api
# Params: api_key=..., date=2023-2026, keywords=['Python', 'Web API', 'Scopus', 'bibliographic survey'], combination=Web API, ratio=80
# Survey: scopus_total=3126, items_per_page=25, pages_count=126, total_retrieved=3126, total_final=3113, loss=13 (0.42%)
# Source: data retrieved from Scopus APIs on 2026-08-03 via http://api.elsevier.com and http://www.scopus.com.
```

**Tradução do Exemplo:**

```txt
# Gerado Por: ...
# Parâmetros: ...
# Levantamento: ...
# Fonte: os dados foram obtidos das APIs da Scopus em 2026-08-03 através de <http://api.elsevier.com> e <http://www.scopus.com>.
```

> [!TIP]
> <a href="./docs/assets/data/example.csv" download="example.csv">Baixe um arquivo CSV de exemplo de levantamento</a> e dê uma olhada.

### 5.3. Performance (v3.2.6)

| Total | Tempo de processamento | Perda     | Vazão        | Latência     |
| ----- | ---------------------- | --------- | ------------ | ------------ |
| 8     | 2.36s                  | 0 (0.00%) | 0.295 s/item | 3.39 items/s |
| 36    | 5.92s                  | 0 (0.00%) | 0.164 s/item | 6.08 items/s |
| 106   | 18.70s                 | 1 (0.93%) | 0.174 s/item | 5,72 items/s |
| 284   | 38.47s                 | 2 (0.70%) | 0.134 s/item | 7.43 items/s |
| 307   | 42.92s                 | 2 (0.65%) | 0.139 s/item | 7.15 items/s |
| 966   | 128.06s (2.13m)        | 0 (0.00%) | 0.133 s/item | 7.54 items/s |
| 3,126 | 412.03s (6.86m)        | 0 (0.00%) | 0.132 s/item | 7.59 items/s |

O desempenho geral **melhorou significativamente em escala** em comparação com a última versão, gerando uma **aceleração de ~1,75x (aumento de 73% na vazão)** e uma **redução de ~42-45% no tempo de processamento por item** para lotes grandes.

Mais importante ainda, a nova implementação **eliminou a degradação do escalamento**, de modo que a vazão permanece estável em **~7,5 a 7,6 itens/s**, mesmo ao escalar até **3.126 itens**.

O rendimento em escala aumentou de **4,36 itens/s para ~7,59 itens/s** (um **aumento de +74,1%** no trabalho realizado por segundo). Agora leva cerca de **~42% menos tempo** para processar o mesmo tamanho de conjunto de dados.

<br>

## Citação

Se este trabalho o ajudou a obter dados relevantes para pesquisa, por favor cite-o:

📝 **ABNT**

```text
BATISTA, Maurício da Silva. Scopus Survey API: API da Web para levantamento bibliográfico de artigos da Scopus. Versão 3.2.6. [Web API]. GitHub, 2025. Disponível em: https://github.com/mauprogramador/scopus-survey-api. Acesso em: DD MMM. YYYY.
```

<br>

---

Para dúvidas ou questões, entre em contato comigo em <sir.silvabmauricio@gmail.com>.

[Termos de Serviço](./legal/pt_BR/TERMS_OF_SERVICE.md)
&nbsp;&#8226;&nbsp;
[Política de Privacidade](./legal/pt_BR/PRIVACY_POLICY.md)
&nbsp;&#8226;&nbsp;
[Política de Cookies](./legal/pt_BR/COOKIE_POLICY.md)
&nbsp;&#8226;&nbsp;
[Atribuições](./legal/pt_BR/ATTRIBUTIONS.md)

[Licença](./LICENSE)
&nbsp;&#8226;&nbsp;
[Traduções](./TRANSLATIONS.md)
&nbsp;&#8226;&nbsp;
[Última Versão](https://github.com/mauprogramador/scopus-survey-api/releases/latest)
&nbsp;&#8226;&nbsp;
[Changelog](./CHANGELOG.md)
