# Requisitos

## API Key

Você deve obter uma `Api Key` para usar a [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"} e pesquisar artigos. Esta `Api Key` não possui espaços e é composta por 32 caracteres contendo apenas letras e números. Ela pode ser obtida acessando o [Elsevier Developer Portal](https://dev.elsevier.com/){:target="_blank"}, clicando no botão **I want an API Key** e realizando seu cadastro.

![Elsevier Portal](../images/elsevier-portal.png)

Se você faz parte de uma instituição de ensino, você pode tentar confirmar se sua instituição está registrada na [Elsevier](https://www.elsevier.com/pt-br){:target="_blank"} para fazer login através de sua organização, ou também pode tentar se registrar com seu e-mail acadêmico.

## Palavras-chave

Com base no tema ou assunto de sua pesquisa, você deve selecionar no mínimo duas e no máximo quatro `Palavras-chave`, que serão utilizadas como parâmetros e filtros na busca de artigos na API. Elas serão pesquisadas simultaneamente no título, resumo e palavras-chave dos artigos. Cada `Palavra-chave` deve ser escrita em inglês, contendo apenas letras, números, espaços e sublinhados, com mínimo de 2 e máximo de 20 caracteres.
