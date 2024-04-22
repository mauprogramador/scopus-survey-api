# Web Scraping

Após obter os dados de cada artigo na [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}, o próximo passo é obter informações sobre os `autores` e o `resumo` de cada artigo, pois normalmente isso não é fornecido pela própria **API**. Para fazer isso, precisamos fazer uma solicitação usando o `Scopus ID` que obtemos da **API** para obter a [página de visualização do artigo no Scopus](https://www.scopus.com/home.uri?zone=header&origin=recordpage){:target="\_blank"}, a solicitação irá recuperar esta página como um modelo HTML, que enviaremos à biblioteca [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/){:target="\_blank"} para raspagem e recuperação, e posteriormente formatar as informações de que necessitamos.

![Article Preview Page](../images/article-preview-page.png)

## URL do Artigo

Este é a URL base da página de visualização do artigo.

```text
https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=...&origin=inward
```

Este é um exemplo de URL com `0037368024` como ID do artigo Scopus.

```text
https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=0037368024&origin=inward
```

!!! note

    [Clique aqui](https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=0037368024&origin=inward){:target="\_blank"} e veja um exemplo de página de visualização de artigo.

## Cabeçalhos da Página do Artigo

Como a página do artigo é mantida para a [Elsevier](https://www.elsevier.com/pt-br){:target="\_blank"} pela [Cloudflare](https://www.cloudflare.com/pt-br/){:target="\_blank"}, precisamos enviar os cabeçalhos apropriados na solicitação para não obter um [acesso proibido](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status/403){:target="\_blank"}, permissão negada ou algum [outro erro](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses){:target="\_blank"}.

```json
"Cache-Control": "no-cache",
"Pragma": "no-cache",
"Referer": "https://www.scopus.com/",
"Connection": "keep-alive",
"Content-Type": "text/plain",
"Origin": "https://www.scopus.com",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
```
