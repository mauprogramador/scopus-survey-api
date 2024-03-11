# Hooks and Actions

No desenvolvimento de uma aplicação, é comum o uso de diversas tecnologias para assegurar uma boa condição do código e do funcionamento desta, para isso podemos utilizar ferramentas para checagem e de integração quando certas ações importantes ocorrem no versionamento de código.

## Git Hooks

Abaixo esta o script do [Git Hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks){:target="\_blank"} do **lado do cliente** usado nesta **API**, é chamado de `pre-commit` porque ele é o primeiro que será executado automaticamente localmente quando ocorrer um _commit_, e irá executar determinadas ações de checagem dependendo dos arquivos que foram alterados e que estão sendo comitados.

- Executa o **Lint** quando arquivos da pasta `app` forem comitados.
- Executa o **Lint** quando arquivos da pasta `tests` forem comitados.
- Executa a **Auditoria de Vulnerabilidade** quando arquivos da pasta `requirements` forem comitados, o que significa que novas bibliotecas, pacotes ou dependências foram instaladas.
- Executa os **Testes** de qualquer forma, garantindo que tudo esteja funcionando.

```sh title="pre-commit"
#!/bin/bash

if git diff --cached --name-only | grep -q '^app/'; then
  make lint
fi

if git diff --cached --name-only | grep -q '^tests/'; then
  make lint-tests
fi

if git diff --cached --name-only | grep -q '^requirements/'; then
  make audit
fi

make test
```

## GitHub Actions

No **lado do servidor**, esta **API** usa o [GitHub Actions](https://github.com/features/actions){:target="\_blank"} para criar **fluxos de trabalho** que serão acionados automaticamente quando um evento `push` ocorrer no repositório remoto do [GitHub](https://github.com/){:target="\_blank"}, automatizando os trabalhos de verificação e implantação para executarem automaticamente.

### Trabalho de Verificação

Para **Linting e Teste**, ele verificará o repositório, configurará o [Python](https://www.python.org/){:target="\_blank"}, instalará o [Poetry](https://python-poetry.org/){:target="\_blank"}, carregará o [Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"} em cache e instalará todas as dependências necessárias, como [Pytest](https://docs.pytest.org/en/8.0.x/contents.html){:target="\_blank"} e [Pylint](https://pylint.readthedocs.io/en/stable/){:target="\_blank"}, para realizar operações de _lint_ e teste no código, garantindo que tudo esteja bem.

### Trabalho de Documentação

Para **implantar e publicar** a documentação da **API**, ele verificará o repositório, configurará o [Python](https://www.python.org/){:target="\_blank"}, carregará o [Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"} em cache e instalará as dependências necessárias, como [MkDocs-Material](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"}, para realizar operações de implantação e publicação usando [MkDocs](https://www.mkdocs.org/){:target="\_blank"}.

Nós utilizamos as bibliotecas [MkDocs](https://www.mkdocs.org/){:target="\_blank"} e [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"} para configurar, fazer o deploy e [publicar](https://squidfunk.github.io/mkdocs-material/publishing-your-site/){:target="\_blank"} o site estático da documentação, escrita em [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax){:target="\_blank"}, e que será hospedado no [GitHub Pages](https://pages.github.com/){:target="\_blank"} no domínio `github.io` do [GitHub](https://github.com/){:target="\_blank"}.
