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

> **Nota:** Esta tradução é fornecida apenas para conveniência e acessibilidade, prevalecendo a [versão em inglês](./README.md) deste documento, para a qual você deve recorrer em caso de discrepâncias.

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul &nbsp;&#8226;&nbsp; [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Tecnologia em Análise e Desenvolvimento de Sistemas &nbsp;&#8226;&nbsp; [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>
Dados fornecidos pela [Scopus](https://www.scopus.com)® &nbsp;&#8226;&nbsp; © [Elsevier](https://www.elsevier.com)

- Documentação: <https://mauprogramador.github.io/scopus-survey-api/>
- API da Web: <http://127.0.0.1:8000/v2/scopus-survey/en-US/search-articles>
- _Swagger UI_: <http://127.0.0.1:8000/>

---

## 1. Visão Geral

Esta **API da web** foi projetada para, dentro de suas limitações, realizar **levantamentos bibliográficos sistemáticos utilizando dados da [base de dados Scopus](https://www.elsevier.com/pt-br/products/scopus)**, promovendo o acesso a fontes bibliográficas relevantes e de alta qualidade por meio de uma interface simples e bem documentada, reduzindo assim a barreira inicial de entrada para **estudantes** e acadêmicos.

Como uma ferramenta [gratuita e não comercial de automação acadêmica](https://dev.elsevier.com/academic_research_scopus.html), a aplicação integra **múltiplos critérios de seleção**, incluindo múltiplos parâmetros de consulta, combinações de palavras-chave e [busca Booleana](https://dev.elsevier.com/sc_search_tips.html), com **mecanismos** para recuperação, validação, serialização e filtragem personalizadas de **grandes volumes de dados** das [APIs da Scopus](https://dev.elsevier.com/sc_apis.html).

Dessa forma, apenas os **dados mais relevantes e recentes** serão mantidos e retornados em um **arquivo CSV**, sendo adequados para estudos e levantamentos bibliométricos, pesquisas, [revisões sistemáticas](https://pt.wikipedia.org/wiki/Revis%C3%A3o_sistem%C3%A1tica), etc., permitindo que os alunos reúnam rapidamente um conjunto de fontes de literatura revisadas por pares para uma tese ou projeto.

---

## 2. Configuração

Crie um arquivo `.env` para configurar as seguintes opções:

| Parâmetro      | Descrição                                                                                          | _Default_   |
| :------------- | :------------------------------------------------------------------------------------------------- | :---------- |
| `HOST`         | Define o endereço do _host_ no qual a aplicação será executada.                                    | `127.0.0.1` |
| `PORT`         | Define a porta do servidor na qual a aplicação será executada.                                     | `8000`      |
| `RELOAD`       | Ativa o recarregamento automático, em caso de alterações nos arquivos, para desenvolvimento local. | `false`     |
| `WORKERS`      | Define o número de processos de trabalho.                                                          | `1`         |
| `LOGGING_FILE` | Ativa o salvamento de _logs_ em arquivos.                                                          | `false`     |
| `DEBUG`        | Ativa o modo de depuração e os _logs_ de depuração.                                                | `false`     |
| `PROGRESS_BAR` | Exibe a barra de progresso do consumo das APIs.                                                    | `true`      |

- As opções `RELOAD` e `WORKERS` são **mutuamente exclusivas**.

- Configurar o `HOST` para `0.0.0.0` torna a aplicação disponível externamente.

> [!NOTE]
> O endereço `0.0.0.0` não é um domínio válido para a política **Cross-Origin-Opener-Policy**, use `localhost` em vez disso.

- Defina o parâmetro `WORKERS` para iniciar **múltiplos processos do servidor**. **Máximo de 4**.

- Desative a barra de progresso ao executar em produção.

> [!TIP]
> Dê uma olhada no arquivo [`.env.example`](./.env.example).

---

## 3. Execução

### 3.1. Com o Poetry ou Pip

Você precisará do [Python3.12](https://www.python.org/downloads/release/python-31211/) com o [Pip](https://pip.pypa.io/en/stable/installation/) e o [Venv](https://docs.python.org/3/library/venv.html) instalados.

```bash
# Crie um novo ambiente virtal (Venv)
python3.12 -m venv .venv

# Ative o Venv
source .venv/bin/activate

# Atualize o Pip
(.venv) pip install --upgrade pip

# Instale o pacote Wheel
(.venv) pip3 install wheel

# Instale as dependências com Poetry [1]
(.venv) pip3 install poetry
(.venv) make install

# Instale as dependências com Pip [2]
(.venv) pip3 install -r requirements/requirements.txt

# Execute o App localmente
(.venv) make run
```

### 3.2. Com o Docker

Você precisará do [Docker](https://www.docker.com/) instalado.

```bash
# Execute o App em Contêiner Docker
make docker
```

---

## 4. Informações Importantes

### 4.1. Fonte de Dados

Declaramos que todo o uso do [banco de dados](https://www.elsevier.com/products/scopus) [Scopus](https://www.scopus.com)® e suas [APIs](https://dev.elsevier.com/sc_apis.html), de propriedade e mantidos pela © [Elsevier B.V.](https://www.elsevier.com/), destina-se exclusivamente à [pesquisa acadêmica não comercial](https://dev.elsevier.com/academic_research_scopus.html), **sem implicar endosso ou afiliação**, e está sujeito aos [nossos Termos](./legal/pt_BR/TERMS_OF_SERVICE.md), bem como aos [Termos da Elsevier](https://www.elsevier.com/legal/elsevier-website-terms-and-conditions) e à [Política da Scopus](https://dev.elsevier.com/academic_research_scopus.html). Todos os dados que manipulamos são obtidos **"NO ESTADO EM QUE SE ENCONTRAM"** e, portanto, apesar de sua reconhecida confiabilidade, não garantimos nem assumimos responsabilidade por quaisquer erros ou imprecisões nos dados do banco de dados Scopus.

> [!CAUTION]
> **É estritamente proibido o uso indevido ou a tentativa de uso indevido de dados obtidos das APIs da Scopus, em violação ao [Contrato de Serviço de API da Elsevier](https://dev.elsevier.com/policy/API-service-agreement.pdf).**

### 4.2. Manipulação de Dados

Em geral, os dados serão preservados sem que haja qualquer alteração direta, porém, como são obtidos **"TAL COMO ESTÃO"**, precisarão ser devidamente validados com base nos campos das respostas HTTP das APIs:

- Aqueles que retornaram algum valor serão mantidos como estão;
- Aqueles que não retornaram valor algum serão definidos como "`nulos`" por padão;
- O campo "`autores`" será definido como o primeiro autor ("`dc:creator`") ou todos os autores ("`authors`") concatenados, dependendo do que for retornado

Por fim, os documentos serão **filtrados e removidos** na seguinte ordem:

1. Duplicatas exatas, sendo mantido o primeiro.
2. Documentos com o mesmo título e mesmo(s) autor(es), sendo mantido o primeiro.
3. Documentos do mesmo(s) autor(es) com títulos semelhantes, sendo mantido o documento com a data de publicação mais recente.

### 4.3. Busca

De acordo com o [Contrato de Serviço de API](https://dev.elsevier.com/policy/API-service-agreement.pdf) e as [Políticas de Uso](https://dev.elsevier.com/policy.html), a **Elsevier** fornecerá uma **Chave de API** que lhe concede uma licença limitada para usar as [APIs da Scopus](https://dev.elsevier.com/sc_apis.html), permitindo que você se autentique corretamente para consultar o banco de dados da Scopus. Ela pode ser obtida acessando o [Portal do Desenvolvedor da Elsevier](https://dev.elsevier.com/) e se cadastrando. Se você faz parte de uma **instituição de ensino**, pode tentar [acessar usando o e-mail institucional ou acadêmico da sua organização](https://www.scopus.com/signin.uri).

Sobre os campos que utilizamos na pesquisa para produzir resultados mais relevantes:

1. O [campo combinado "`TITLE-ABS-KEY`"](https://dev.elsevier.com/sc_search_tips.html) para **pesquisar simultaneamente combinações de palavras-chave em resumos, palavras-chave e títulos, e recuperar as literaturas onde elas são encontradas**.
2. Os campos "`date`" e "`sort`" para delimitar o período de interesse para as publicações e ordenar por ano e data de publicação e por relevância.
3. Outros campos **adicionais opcionais** que podemos enviar combinando-os com o [operador booleano "`AND`"](https://dev.elsevier.com/sc_search_tips.html), como área temática e idioma.

As buscas serão realizadas da seguinte forma:

1. Obter o número total de resultados encontrados para cada combinação de palavras-chave, concatenando-os com o [operador booleano "`AND`"](https://dev.elsevier.com/sc_search_tips.html).
2. Realizar efetivamente a busca final com a combinação selecionada e obter o **ID da Scopus** de cada resultado na paginação.
3. Recuperar um conjunto de dados completo com metadados abrangentes pelo **ID da Scopus**, obtendo todos os campos com informações bibliográficas relevantes para cada resultado da pesquisa anterior.

### 4.4. Rede Institucional <img src="https://img.shields.io/badge/Required-dc3545" alt="Required">

Por favor esteja ciente de que a **Chave de API** só será autenticada corretamente se você a enviar enquanto estiver usando a **rede da sua instituição acadêmica**, que deve estar **registrada na Elsevier**. Isso **não inclui** acesso por <abbr title="Rede Privada Virtual">VPN</abbr> ou proxy. Portanto, se você estiver **totalmente remoto** e **fora do campus**, alguns dados poderão **não ser retornados**.

### 4.5. Cota e Taxa de Limitação <img src="https://img.shields.io/badge/Important-ffc107" alt="Important">

Há um **limite máximo para o número de solicitações** que podemos fazer às [APIs Scopus](https://dev.elsevier.com/sc_apis.html) usando sua **Chave de API**. Essa **cota de solicitações é redefinida a cada sete dias**, é **exclusiva para cada API** e você pode **verificar sua disponibilidade no painel de detalhes após cada operação**. Se as solicitações **excederem a cota ou a taxa de limitação**, um **erro será retornado**. Consulte as [Configurações da Chave de API](https://dev.elsevier.com/api_key_settings.html).

| API da Scopus          | Cota Semanal | Taxa de Limitação |
| ---------------------- | ------------ | ----------------- |
| Search API             | 20,000       | 9req/s            |
| Abstract Retrieval API | 10,000       | 9req/s            |

### 4.6. Client HTTP Assíncrono

Para evitar ultrapassar o [limite de taxa e cota de solicitações da API](https://dev.elsevier.com/api_key_settings.html) ao realizar diversas solicitações, construímos um cliente HTTP assíncrono com mecanismos de controle de fluxo e tratamento de erros para lidar com esse grande volume de solicitações simultaneamente (concorrência), respeitando os limites da API com base no **número total de solicitações a serem feitas**. Empregamos:

- `asyncio.Semaphore` e `asyncio.sleep` para controlar a concorrência e inserir _delays_ adicionais;
- `aiohttp.ClientSession` e `aiohttp.ClientTimeout` para gerenciar a sessão do cliente, o _timeout_ e a conexão;
- `aiolimiter.AsyncLimiter` para limitação de taxa;
- `aiohttp_retry.RetryClient` e `aiohttp_retry.JitterRetry` para mecanismos de repetição automática (_retry_), com _jitter_, _backoff_ e _timeout_.

Para **_retries_** serão feitas até **3 tentativas**, e para **_rate limiting_** (taxa de limitação) será utilizada uma estratégia dinâmica baseada na quantidade de solicitações a serem feitas.

| Número de Solicitações | Taxa de Solicitação | Fator de Recuo | Atraso | Solicitações Concorrentes |
| :--------------------- | :------------------ | :------------- | :----- | :------------------------ |
| 100                    | 8.0 req/s           | 2.0            | 0.0s   | 10                        |
| 500                    | 6.0 req/s           | 3.0            | 0.15s  | 5                         |
| 1000                   | 5.0 req/s           | 3.5            | 0.25s  | 3                         |
| 2000                   | 4.0 req/s           | 4.5            | 0.35s  | 2                         |

---

## 5. Campos

### 5.1. Formulário Multi-Passos

- **PASSO 1 - Chave de API**

Neste passo você deverá inserir a **Chave de API**, emitida pela Elsevier, principal parâmetro sem o qual a aplicação não poderá ser executada, pois é necessário para correta autenticação e uso das APIs da Scopus, e se você já realizou um levantamento antes, também poderá **tentar baixar o arquivo CSV gerado anteriormente**, que ainda pode estar armazenado.

- **PASSO 2 - Parâmetros Adicionais**

Neste passo você poderá **inserir e selecionar vários campos** que serão combinados com o operador `AND` e enviados, quando preenchidos, como parâmetros para realizar uma consulta booleana na base Scopus e produzir resultados mais relevantes.

- **PASSO 3 - Combinação de Palavras-chave**

Neste passo você deverá selecionar as **palavras-chave**, com base no tema ou assunto da sua pesquisa, que serão concatenadas pelo operador booleano `AND` gerando todas as combinações possíveis, para enfim levantar o **total de documentos encontrados** na Scopus, buscando nos resumos, palavras-chave e títulos, **para cada combinação**, delimitando o escopo da pesquisa com base na opção de combinação e no total retornado.

- **PASSO 4 - Levantamento Final**

Neste último passo, todos os campos preenchidos serão submetidos para à realização do levantamento sistemático das informações, removendo duplicatas e filtrando documentos semelhantes, restando apenas os dados mais relevantes e recentes.

### 5.2. Campos Obrigatórios <img src="https://img.shields.io/badge/Required-dc3545" alt="Required">

- **Chave de API:** A Chave da API emitida pela Elsevier, obtida ao acessar o Portal da Elsevier e se cadastrando.
- **Palavras-chave:** As Palavras-chave, com um **mínimo de duas** (obrigatório) e um **máximo de quatro**, que os documentos que você está buscando contêm. Devem ser **escritos em inglês**, com no **máximo 70 caracteres**, podendo conter **letras**, **números**, **espaços**, **hifens**, **sublinhados**, [**frases**, **curingas** e os **operadores booleanos `OR` e `AND NOT`**](https://dev.elsevier.com/sc_search_tips.html).

> [!WARNING]
> Como **`AND NOT`** pode [gerar resultados inesperados](https://dev.elsevier.com/sc_search_tips.html), ele deve ser usado no **último campo**.

- **Combinação:** A opção de combinação de palavras-chave que melhor se adapta às suas necessidades com base no total de documentos encontrados.

### 5.3. Campos Opcionais <img src="https://img.shields.io/badge/Optional-6C757D" alt="Optional">

- **Data:** O intervalo de anos, dos últimos dez anos até o ano atual, como alvo de interesse dos artigos publicados. Por padrão, consideram-se os últimos três anos.
- **Doctype:** O tipo em que o documento é classificado.
- **Pubstage:** A fase de publicação do documento.
- **Idioma:** O idioma em que o documento original foi escrito.
- **Acesso Aberto:** Se o conteúdo indexado é de acesso aberto ou não.
- **Srctype:** O tipo de fonte de onde o documento se origina.
- **Subjarea:** A área temática em que o documento está classificado.
- **Páginas:** Se o documento é curto (até 4 páginas, como notas de pesquisa) ou completo (5 páginas ou mais), pelo número de páginas.
- **Limiar de Similaridade:** O valor do limiar, no intervalo de 0 a 100, usado para filtrar documentos com o(s) mesmo(s) autor(es) e títulos semelhantes, mantendo aquele com a data de publicação mais recente.

---

## 6. Resultados

### 6.1. Campos Obtidos

Campos mapeados do arquivo CSV

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
| `citedby-count`           | Citations                | Contagem de citações                           |

### 6.2. Metadados do CSV

Como o resultado do levantamento é um arquivo CSV, que é essencialmente um conjunto de dados obtido das APIs da Scopus, devemos [**reconhecer** tanto o Scopus quanto a Elsevier como **fontes de dados**](https://dev.elsevier.com/tecdoc_attribution_scopus.html). Portanto, adicionaremos alguns metadados no **início do arquivo (4 linhas) como comentários** indicando os parâmetros utilizados, detalhes da pesquisa e a data em que os dados foram obtidos.

**Exemplo:**

```txt
# GeneratedBy: ScopusSurveyAPI https://github.com/mauprogramador/scopus-survey-api
# Params: api_key=..., date=2022-2025, keywords=['Python', 'Web API', 'Scopus', 'bibliographic survey'], combination=Python AND Web API AND Scopus, ratio=80
# Survey: total=5, items_per_page=5, pages_count=1, loss=0doc / 0.00%
# Source: data retrieved from Scopus APIs on November 22, 2025 via http://api.elsevier.com and http://www.scopus.com.
```

> _Tradução do Exemplo:_
>
> ```txt
> # Gerado Por: ...
> # Parâmetros: ...
> # Levantamento: ...
> # Fonte: Os dados foram obtidos das APIs da Scopus em 22 de Novembro de 2025, através de <http://api.elsevier.com> e <http://www.scopus.com>.
> ```

É possível realizar mais de um levantamento utilizando as combinações de palavras-chave da tabela. Por isso, a fim de evitar confusão, salvaremos os arquivos CSV com a combinação usada para produzir aquele resultado por padrão.

**Exemplo:**

| Combinação                    | Nome do Arquivo                           |
| ----------------------------- | ----------------------------------------- |
| Python AND Scopus             | [API Key]\_python-scopus_docs.csv         |
| Python AND Scopus AND Web API | [API Key]\_python-scopus-web-api_docs.csv |

### 6.3. Visualização

Para visualizar os documentos (pelo menos a pré-visualização), você pode usar:

- A **URL** na coluna **_Article Preview Page URL_**:<br>
  <https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=[SCOPUS_ID]&origin=inward>

- O **Identificador de Objeto Digital (DOI)** na coluna **DOI**:<br>
  <https://doi.org/[DOI]><br>

### 6.4. Performance

| Palavras-chave       | Total encontrado | Tempo de Processamento | Perda        |
| -------------------- | ---------------- | ---------------------- | ------------ |
| Web API AND Scopus   | 25               | 3.63s                  | 0doc / 0.00% |
| Python AND Scopus    | 141              | 19.26s                 | 1doc / 0.71% |
| Bibliographic Survey | 1073             | 246.38s (4.10m)        | 7doc / 0.65% |

> [!TIP]
> <a href="./docs/assets/data/example.csv" download="example.csv">Baixe um arquivo CSV de exemplo de levantamento</a> e dê uma olhada.

---

Para dúvidas ou preocupações, entre em contato comigo em <sir.silvabmauricio@gmail.com>.

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
