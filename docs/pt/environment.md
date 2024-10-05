# Ambiente

## Configuração

| **Parâmetro**  | **Descrição**                                                                                                       | **Default** |
| -------------- | ------------------------------------------------------------------------------------------------------------------- | ----------- |
| `debug`        | Habilita a saída dos logs de depuração                                                                              | `false`     |
| `logging_file` | Habilita o salvamento dos registros dos logs em arquivo. Isso criará uma pasta `.logs`                              | `false`     |
| `host`         | Vincula o soquete a este endereço de host.<br>Defina `0.0.0.0` para tornar a aplicação disponível em sua rede local | `127.0.0.1` |
| `port`         | Vincula a um soquete e executa a aplicação com esta porta                                                           | `8000`      |
| `reload`       | Habilita o recarregamento automático da aplicação quando os arquivos são modificados                                | `false`     |

Você pode configurar alguns parâmetros para a aplicação no arquivo `pyproject.toml`, tais como:

```toml title="pyproject.toml" linenums="81"
[application]
debug = false
logging_file = false
host = "127.0.0.1"
port = 8000
reload = false
```

Você também pode definir [variáveis de ambiente](https://en.wikipedia.org/wiki/Environment_variable){:target="\_blank"} para **substituir as configurações padrão** ao executar a aplicação **localmente** ou em um **contêiner Docker**.

```.env title=".env" linenums="1"
DEBUG=false

LOGGING_FILE=false

HOST=127.0.0.1

PORT=8000

RELOAD=false
```

## Ambiente Python

É necessário preparar um ambiente com as dependências corretas para trabalhar corretamente com cada área da aplicação. Para fazer isso, você precisa instalar o [Python3 `v3.11`](https://www.python.org/downloads/release/python-3117/){:target="\_blank"} com [Venv]({{links.pythonDocs}}/venv.html){:target="\_blank"} e [Pip](https://pip.pypa.io/en/stable/installation/){:target="\_blank"}.

!!! info

    Este projeto usa o [Poetry](https://python-poetry.org/){:target="\_blank"} para empacotar e gerenciar dependências do Python.

!!! tip

    Você também pode usar [Docker](https://www.docker.com/){:target="\_blank"} para executar a aplicação.

### Configurar o [Ambiente Virtual]({{links.pythonDocs}}/venv.html){:target="\_blank"}

```zsh
# Configure o Venv
make setup

# Ative o Venv
source .venv/bin/activate
```

## Dependências

### Ambiente Completo

:material-arrow-down-bold-box: Instale **todas** as dependências.

=== "com Poetry"

    ```zsh
    (.venv) poetry install
    ```

=== "com Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-all.txt
    ```

## Ambiente da Aplicação

:material-arrow-down-bold-box: Instale apenas as dependências da **aplicação**.

=== "com Poetry"

    ```zsh
    (.venv) make install
    ```

=== "com Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements.txt
    ```

<br>
:material-play-circle: Execute a aplicação

=== "Localmente"

    ```zsh
    # Execute a aplicação Localmente
    (.venv) make run
    ```

=== "Docker"

    ```zsh
    # Execute a aplicação em um Contêiner Docker
    make docker
    ```

### Ambiente de Desenvolvimento

:material-arrow-down-bold-box: Instale apenas as dependências de **desenvolvimento**.

=== "com Poetry"

    ```zsh
    (.venv) poetry install --only dev
    ```

=== "com Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-dev.txt
    ```

<br>
:material-play-circle: Execute a [Formatação](https://code.visualstudio.com/docs/python/formatting){:target="\_blank"}, o [Linting](https://code.visualstudio.com/docs/python/linting){:target="\_blank"} e a [Auditoria de Vulnerabilidades](https://en.wikipedia.org/wiki/Code_audit){:target="\_blank"}.

```zsh
# execute a Formatação
(.venv) make format

# execute o Linting
(.venv) make lint

# execute o Linting nos Testes
(.venv) make lint-tests

# execute a Auditoria de Vulnerabilidades
(.venv) make audit
```

## Ambiente dos Testes

:material-arrow-down-bold-box: Instale apenas as dependências dos **testes**.

=== "com Poetry"

    ```zsh
    (.venv) poetry install --only test
    ```

=== "com Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-test.txt
    ```

<br>
:material-play-circle: Execute os testes e verifique a cobertura dos testes

=== "Localmente"

    ```zsh
    # Execute o Pytest no Venv
    (.venv) make test

    # Execute o Coverage no Venv
    (.venv) make coverage
    ```

=== "Docker"

    ```zsh
    # Execute o Pytest no Docker
    make test-docker

    # Execute o Coverage no Docker
    make coverage-docker
    ```

## Ambiente da Documentação

:material-arrow-down-bold-box: Instale apenas as dependências da **documentação**.

=== "com Poetry"

    ```zsh
    (.venv) poetry install --only docs
    ```

=== "com Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-docs.txt
    ```

<br>
:material-play-circle: Execute a documentação do [Mkdocs](https://www.mkdocs.org/){:target="\_blank"}.

Execute Localmente e acesse a página web em <http://127.0.0.1:8000>{:target="\_blank"}.

```zsh
# Servir MkDocs
(.venv) make docs
```

## Arquivos de Requisitos

Você pode gerar vários [arquivos de requisitos](https://pip.pypa.io/en/stable/reference/requirements-file-format/){:target="\_blank"} para diferentes finalidades.

```zsh
# Requisitos apenas para as dependências da Aplicação
(.venv) make req

# Requisitos para a Aplicação com as dependências de Desenvolvimento
(.venv) make req-dev

# Requisitos para as dependências da Documentação
(.venv) make req-docs

# Requisitos para as dependências dos Testes
(.venv) make req-test

# Requisitos para Todas as dependências
(.venv) make req-all
```
