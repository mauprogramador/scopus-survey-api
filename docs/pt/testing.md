# Teste

## Testes automatizados

Você pode [configurar](./environment.md#ambiente-dos-testes) e usar o [Vs Code para testar](https://code.visualstudio.com/docs/python/testing){:target="_blank"} todos os scripts com [Pytest](https://docs.pytest.org/en/8.0.x/){:target="_blank"} e o [Coverage](https://coverage.readthedocs.io/en/7.4.3/){:target="_blank"}:

```bash
# Execute o Pytest no Venv
(.venv) $ make test

# Execute o Pytest no Docker
$ make test-docker

# Execute o Coverage no Venv
(.venv) $ make coverage

# Execute o Coverage no Docker
$ make coverage-docker
```

![Pytest](../images/pytest.png)

## Testes de Requisição

Você pode instalar a [extensão Rest Client do Vs Code](https://github.com/Huachao/vscode-restclient){:target="_blank"} para configurar e enviar requisições para testar a [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"}. Acesse o arquivo `testes/client.http`, insira sua `Api Key` e envie as requisições:

![Rest Client](../images/rest-client.png)
