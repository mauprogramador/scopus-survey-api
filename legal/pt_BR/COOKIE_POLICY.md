# Política de Cookies

**Scopus Survey API** - _API da Web para levantamento bibliográfico de artigos da Scopus_

> _Última atualização: 28 de Novembro de 2025_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

> **Nota:** Esta tradução é fornecida apenas para conveniência e acessibilidade, prevalecendo a [versão em inglês](./../en_US/COOKIE_POLICY.md) deste documento, para a qual você deve recorrer em caso de discrepâncias.

---

Este acordo (**"Política de Cookies"**) explica os cookies e sob quais condições você e a Scopus Survey API (**"Serviço"**), fornecida por nós (**"nós"**, **"nos"**, **"nosso"**, ou **"nossos"**), poderá gerir as preferências e a utilização de cookies para melhorar a sua experiência.

<br>

## 1. O que são Cookies?

Cookies são pequenos arquivos armazenados no seu dispositivo (computador, _tablet_ ou telemóvel) quando visita um website. Eles ajudam o website a funcionar de forma mais eficiente, fornecendo informações de relatórios, reconhecendo o seu dispositivo e memorizam informações sobre a sua visita, como as suas preferências ou informações de _login_. É por isso que são amplamente utilizados como prática padrão na maioria dos websites profissionais. Os cookies definidos pelo proprietário do website são chamados de **"cookies primários"**.

## 2. Como Utilizamos os Cookies

O único tipo de cookies que o nosso Serviço implementa e gerencia são os chamados **"essenciais"** ou **"estritamente necessários"**, porque são necessários por razões técnicas, uma vez que permitem a funcionalidade principal para que o nosso Serviço funcione corretamente.

Utilizamos apenas dois cookies **primários** e **essenciais**:

- **Cookie de Sessão**: Utiliza o [Middleware de Sessão do Starlette](https://www.starlette.io/middleware/#sessionmiddleware) para adicionar sessões HTTP baseadas em cookies criptografados para rastrear e controlar o tempo da **Sessão**.
- **Token de Cookie**: Estritamente necessário para autenticação e proteção contra **CSRF** (Cross-Site Request Forgery). Gerencia automaticamente um **Token CSRF**, criado usando o serializador [URLSafeTimedSerializer da ItsDangerous](https://itsdangerous.palletsprojects.com/en/stable/url_safe/), por meio de cabeçalhos HTTP, cookies, parâmetros de consulta e sessão, sendo essencial para manter interações seguras dentro do Serviço.

## 3. Duração dos Cookies

- **Cookies de Sessão**: Temporários e expiram ao fechar o navegador.
- **Cookies Persistentes**: Permanecem no seu dispositivo por um período determinado ou até que você os exclua.

| Cookie       | Tipo                    | Duração             |
| ------------ | ----------------------- | ------------------- |
| `session`    | Essencial / Sessão      | Sessão do navegador |
| `csrf-token` | Essencial / Persistente | 1 hora              |

## 4. Como posso controlar os cookies?

Nossos cookies essenciais **NÃO PODEM SER REJEITADOS**, pois são estritamente necessários para o Serviço.

Você tem controle sobre como os cookies são gerenciados no seu dispositivo, impedindo que sejam instalados ao ajustar as configurações do seu navegador para aceitar ou rejeitar cookies, ou para alertá-lo quando um cookie estiver sendo instalado. Esteja ciente de que desativar nossos cookies afetará a funcionalidade do Serviço, fazendo com que ele não funcione como esperado.

**Configurações do navegador:** você geralmente encontra essas configurações no menu **"Opções"** ou **"Preferências"** do seu navegador. Para obter mais informações, visite a página de suporte do seu navegador:

- **Chrome:** [Excluir, permitir e gerenciar cookies no Chrome](https://support.google.com/chrome/answer/95647?hl=pt-BR).
- **Firefox:** [Proteção aprimorada contra rastreamento no Firefox para desktop](https://support.mozilla.org/pt-BR/kb/protecao-aprimorada-contra-rastreamento-firefox-desktop?redirectslug=enable-and-disable-cookies-website-preferences&redirectlocale=en-US).
- **Safari:** [Limpe os cookies do Safari no Mac](https://support.apple.com/pt-br/guide/safari/sfri11471/18.0/mac/15.0).
- **Edge:** [Gerence cookies no Microsoft Edge](https://support.microsoft.com/pt-br/windows/gerencie-cookies-no-microsoft-edge-exibir-permitir-bloquear-excluir-e-usar-168dab11-0753-043d-7c16-ede5947fc64d).
- **Opera:** [Gerenciar cookies em páginas](https://help.opera.com/en/latest/web-preferences/#cookies).
- **Brave:** [Como faço para limpar cookies e dados do site no Brave?](https://support.brave.app/hc/pt/articles/360048833872-Como-fa%C3%A7o-para-limpar-cookies-e-dados-do-site-no-Brave).

## 5. Atualizações

Podemos atualizar esta Política de Cookies periodicamente para refletir alterações nos requisitos legais ou em nosso uso de cookies. Notificaremos os usuários sobre quaisquer alterações significativas por meio de nosso [repositório do GitHub](https://github.com/mauprogramador/scopus-survey-api) ou [Documentação](https://mauprogramador.github.io/scopus-survey-api/). Seu uso contínuo do Serviço após tais alterações constitui sua aceitação dos novos Termos.

## 6. Referências

- **Documentação da MDN:** [Cookies HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Guides/Cookies).
- **Cloudflare:** [O que são cookies?](https://www.cloudflare.com/pt-br/learning/privacy/what-are-cookies/).
- **Starlette:** [Middleware de sessão](https://www.starlette.io/middleware/#sessionmiddleware)
- **ItsDangerous:** [Serializador URLSafeTimedSerializer](https://itsdangerous.palletsprojects.com/en/stable/url_safe/).
- **Documentação da MDN:** [Cross-site request forgery (CSRF)](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF).
- **Cloudflare:** [O que é falsificação de solicitação entre sites?](https://www.cloudflare.com/pt-br/learning/security/threats/cross-site-request-forgery/).

## 7. Contato

Para dúvidas ou preocupações sobre a estas Políticas, entre em contato conosco por <sir.silvabmauricio@gmail.com>.
