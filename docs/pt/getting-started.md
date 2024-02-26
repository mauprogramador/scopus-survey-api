# Primeiros Passos

## Clone

Primeiro você precisa clonar o projeto do repositório no GitHub: <https://github.com/mauprogramador/scopus-searcher-api>{:target="_blank"}

No terminal Bash:

```bash
git clone https://github.com/mauprogramador/scopus-searcher-api.git
```

No Vs Code:

> `Ctrl` + `Shift` + `P` > `Git: Clone` > <https://github.com/mauprogramador/scopus-searcher-api.git>{:target="_blank"}

## Execute

Com Python3:

```bash
# Execute a aplicação localmente
$ make run
```

Com Docker:

```bash
# Execute a aplicação no Container do Docker
$ make docker
```

---

## Swagger interativo

Depois de iniciar a aplicação, você pode acessar o [Swagger UI](https://github.com/swagger-api/swagger-ui){:target="_blank"} clicando em: <http://127.0.0.1:8000>{:target="_blank"}

![Swagger](../images/swagger.png)

Selecione o primeiro Endpoint (**GET /scopus-searcher/api/search-articles**) e clique em **Try it out**.

- Insira sua `Api Key` e `Keywords`.
- As `Palavras-chave` devem ser separadas por vírgula.
- É obrigatório o preenchimento do campo da `Api Key` e pelo menos duas `Palavras-chave`.
- O cabeçalho `X-Access-Token` será definido automaticamente, você **não deve** alterá-lo.
- Clique no botão **Execute**.

![Swagger Search](../images/swagger-search.png)

Se algum artigo for encontrado com sucesso, irá retornar um [arquivo CSV](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="_blank"} contendo todas as informações da pesquisa. Você pode clicar no botão **Download** para baixar o arquivo.

![Swagger Success](../images/swagger-success.png)

Caso nenhum artigo seja encontrado, uma mensagem retornará informando o que houve de errado. Você deve primeiro ler e analisar a mensagem e tentar entender o que causou o erro antes de tentar novamente.

![Swagger Error](../images/swagger-error.png)

## Aplicação Web

Depois de iniciar a aplicação, você pode acessar a aplicação Web clicando em: <http://127.0.0.1:8000/scopus-searcher/api>{:target="_blank"}

![Web](../images/web.png)

Na página web, clique nos campos e insira seus dados, certificando-se de que estão corretos.

- Selecione o idioma de sua preferência clicando no símbolo da **Bandeira** (Suporte para `en-us` e `pt-br`).
- Insira sua `Api Key` e `Palavras-chave` nos respectivos campos.
- Insira uma `Palavra-chave` para cada campo..
- É obrigatório o preenchimento do campo da `Api Key` e de pelo menos dois campos das `Palavras-chave`.
- Clique no botão **Procurar Artigos** e aguarde os resultados da pesquisa.

![Web Search](../images/web-search.png)

Se algum artigo for encontrado com sucesso, uma mensagem retornará informando sobre o sucesso e o [arquivo CSV](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="_blank"} contendo todas as informações da pesquisa será baixado automaticamente.

![Web Success](../images/web-success.png)

Caso nenhum artigo seja encontrado, uma mensagem retornará informando o que houve de errado. Você deve primeiro ler e analisar a mensagem e tentar entender o que causou o erro antes de tentar novamente.

![Web Error](../images/web-error.png)

Você também pode verificar no inspecionar [DevTools](https://developer.chrome.com/docs/devtools?hl=pt-br){:target="_blank"} do navegador a resposta da requisição.

![Inspect Error](../images/inspect-error.png)

Todos os campos da página web estão configurados para verificar se as informações de cada respectivo campo estão corretas, portanto você deve estar atento às regras e condições relativas à `Api Key` e às `Palavras-chave` fornecidas na [seção de requisitos](./requirements.md).

Assim que você começar a digitar em um campo, ele lhe dará um feedback automaticamente, então fique atento:

- Lembre-se que é obrigatório o preenchimento do campo da `Api Key` e de pelo menos dois campos das `Palavras-chave`.
- A cor vermelha circulará o campo e uma mensagem será mostrada caso os dados estejam incorretos.
- A cor verde circulará o campo se os dados estiverem corretos.

![Web Validation](../images/web-validation.png)
