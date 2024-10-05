# Requisitos

## Chave da API

Você deve obter uma `Chave da API` para usar as [{{abbr.api}}s da Scopus]({{links.scApis}}){:target="\_blank"} para pesquisar e recuperar as informações dos artigos. Ela **não possui espaços** e é **composta por 32 caracteres** contendo **apenas letras e números**. Pode ser obtida acessando o [Elsevier Developer Portal](https://dev.elsevier.com/){:target="\_blank"}, clicando no botão **I want an API Key** e realizando seu cadastro.

![Elsevier Portal](../assets/img/elsevier-portal.png "Elsevier Portal")

Se você faz parte de uma instituição de ensino, você pode tentar confirmar se sua instituição está registrada na [Elsevier]({{links.elsevier}}){:target="\_blank"} para fazer login através de sua organização, ou você também pode tentar se registrar com seu e-mail acadêmico.

## Palavras-chave

Com base no tema ou assunto de sua pesquisa, você deve selecionar no **mínimo duas** e no **máximo quatro `Palavras-chave`**, que serão utilizadas como parâmetros e filtros na busca simultânea no título, resumo e palavras-chave dos artigos. Cada `Palavra-chave` deve ser **escrita em Inglês**, contendo **apenas letras, números, espaços e sublinhados**, com no **mínimo de 2** e no **máximo de 20 caracteres**.

Exemplo

```text
Computer Vision, Scopus, Machine Learning, Bibliometric
```

## Rede Instituicional

Por favor esteja ciente de que a `Chave da API` só será autenticada corretamente se você submetê-la enquanto estiver dentro da **rede da sua universidade/instituição**, e isso não inclui acesso por {{abbr.vpn}} ou {{abbr.proxy}}. Portanto, se você estiver **totalmente remoto** e **fora do campus**, o **resumo** e **todos os autores** dos artigos **não serão retornados**.
