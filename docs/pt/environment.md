# Ambiente

É necessário preparar um ambiente com as dependências corretas para trabalhar corretamente com cada área da aplicação. Para fazer isso, você precisa instalar o [Python v3.11](https://www.python.org/downloads/release/python-3117/){:target="_blank"} com [Venv](https://docs.python.org/3/library/venv.html){:target="_blank"} e [Pip](https://pip.pypa.io/en/stable/installation/){:target="_blank"} ou instalar o [Docker](https://www.docker.com/){:target="_blank"}.

## Ambiente de Desenvolvimento

Crie o [Ambiente Virtual Python - Venv](https://docs.python.org/3/library/venv.html){:target="_blank"} e instale **todas** as dependências necessárias.

### Pip

```bash
# Crie o Venv
$ make venv v=3.**

# Ative o Venv
$ source .venv/bin/activate

# Instale todas as dependências
(.venv) $ pip3 install -r requirements/requirements-all.txt
```

### Poetry

```bash
# Crie o Venv
$ make venv v=3.**

# Ative o Venv
$ source .venv/bin/activate

# Instale todas as dependências
(.venv) $ make install
```

**Depois de instalar as dependências, você pode [começar](./getting-started.md).**

### Formatação, Linting and Auditoria de Vulnerabilidade

```bash
# Executar formatação
(.venv) $ make format

# Executar linting
(.venv) $ make lint

# Executar linting nos testes
(.venv) $ make lint-tests

# Executar auditoria de vulnerabilidade
(.venv) $ make audit
```

## Ambiente da Aplicação

Crie o [Ambiente Virtual Python - Venv](https://docs.python.org/3/library/venv.html){:target="_blank"} e instale apenas as dependências da **aplicação**.

```bash
# Crie o Venv
$ make venv v=3.**

# Ative o Venv
$ source .venv/bin/activate

# Instale as dependências da aplicação
(.venv) $ pip3 install -r requirements/requirements.txt
```

## Ambiente dos Testes

Crie o [Ambiente Virtual Python - Venv](https://docs.python.org/3/library/venv.html){:target="_blank"} e instale apenas as dependências dos **testes**.

```bash
# Crie o Venv
$ make venv v=3.**

# Ative o Venv
$ source .venv/bin/activate

# Instale as dependências dos testes
(.venv) $ pip3 install -r requirements/requirements-test.txt
```

## Ambiente da Documentação

Crie o [Ambiente Virtual Python - Venv](https://docs.python.org/3/library/venv.html){:target="_blank"} e instale apenas as dependências da **documentação**.

```bash
# Crie o Venv
$ make venv v=3.**

# Ative o Venv
$ source .venv/bin/activate

# Instale as dependências da documentação
(.venv) $ pip3 install -r requirements/requirements-docs.txt
```

### Execute a documentação do [Mkdocs](https://www.mkdocs.org/){:target="_blank"}

Execute localmente e acesse a página da web: <http://127.0.0.1:8000>{:target="_blank"}

```bash
# Execute o MkDocs no Venv
(.venv) $ make docs
```

Execute no Docker e acesse a página web: <http://127.0.0.1:8001>{:target="_blank"}

```bash
# Execute o MkDocs no Docker
$ make docker-docs
```

## Arquivos de requisitos

Você pode gerar vários [arquivos de requisitos](https://pip.pypa.io/en/stable/reference/requirements-file-format/){:target="_blank"} para diferentes finalidades.

```bash
# Requisitos apenas para as dependências da aplicação
(.venv) $ make req

# Requisitos para a aplicação com as dependências de desenvolvimento
(.venv) $ make req-dev

# Requisitos para as dependências da documentação
(.venv) $ make req-docs

# Requisitos para as dependências dos testes
(.venv) $ make req-test

# Requisitos para todas as dependências
(.venv) $ make req-all
```
