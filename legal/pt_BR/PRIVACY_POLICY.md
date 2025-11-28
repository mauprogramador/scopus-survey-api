# Política de Privacidade

**Scopus Survey API** - _API da Web para levantamento bibliográfico de artigos da Scopus_

> _Última atualização: 28 de Novembro de 2025_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

Dados fornecidos pela [Scopus](https://www.scopus.com)®. © [Elsevier](https://www.elsevier.com). Todos os direitos reservados.

> **Nota:** Esta tradução é fornecida apenas para conveniência e acessibilidade, prevalecendo a [versão em inglês](./../en_US/PRIVACY_POLICY.md) deste documento, para a qual você deve recorrer em caso de discrepâncias.

---

Este acordo (**"Política de Privacidade"**) define as condições sob as quais a Scopus Survey API (**"Serviço"**), fornecida por nós (**"nós"**, **"nos"**, **"nosso"**, ou **"nossos"**), coleta e usa suas informações.

<br>

## 1. Informações que Coletamos

### 1.1. Informações que Você nos Fornece

- Sua **Chave de API** da Scopus.
- Todos os parâmetros que você enviar no formulário online.
- Se você entrar em contato conosco diretamente (ex.: por e-mail), coletamos o conteúdo da sua mensagem e suas informações de contato.

### 1.2. Informações Coletadas Automaticamente

Ao acessar e usar o Serviço, nós coletamos automaticamente certas informações que seu navegador ou dispositivo envia, incluindo:

- **Dados de Uso:** Isso pode incluir seu endereço IP, informações do navegador, as páginas do nosso Serviço que você visita, a data e hora da sua visita, o tempo gasto nessas páginas e outros dados de diagnóstico.
- **Cookie de Sessão:** Usamos o [Middleware de Sessão do Starlette](https://www.starlette.io/middleware/#sessionmiddleware) para adicionar sessões HTTP baseadas em cookies criptografados para rastrear e controlar o tempo da **Sessão**.
- **Token de Cookie:** Estritamente necessário para autenticação e proteção contra ataques **CSRF** (Cross-Site Request Forgery). Seu **Token CSRF** é gerenciado automaticamente por meio de cabeçalhos HTTP, cookies, parâmetros de consulta e sessão, e é essencial para manter interações seguras dentro do Serviço.
**Tecnologias de Rastreamento:** Como utilizamos o [Limitador do Slowapi](https://slowapi.readthedocs.io/en/latest/) para controlar a taxa de limite de requisições do Serviço, seu endereço IP será obtido e armazenado por padrão.

### 1.3. Informações de Fontes de Terceiros (Dados da Scopus)

Nosso Serviço consulta e acessa o banco de dados Scopus® por meio da [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl) e da [Scopus Abstract Retrieval API](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl). No entanto, o que é recuperado consiste principalmente em informações de publicações acadêmicas, como títulos de artigos, resumos, detalhes dos autores, citações e palavras-chave, que são conteúdo público ou com licença acadêmica.

Gostaríamos de esclarecer que **não coletamos nem processamos nenhuma informação do usuário por meio das APIs da Scopus, nem processamos nenhuma informação da sua conta**. Os únicos dados da Scopus que utilizamos são a sua **Chave de API**, que não está diretamente vinculada às suas informações pessoais e nem nos permite acessá-las.

O Serviço utiliza sua **Chave de API** apenas para recuperar, validar e filtrar sistematicamente os dados do levantamento para você e retorná-los de forma organizada.

<br>

## 2. Como Utilizamos suas Informações

- **Fornecer e Manter nosso Serviço:** Garantir seu funcionamento adequado e conformidade com a finalidade pretendida.
- **Segurança e Prevenção de Fraudes:** Gerenciar **Tokens de Sessão e CSRF**, detectar e prevenir acessos não autorizados ou atividades maliciosas.
- **Aprimorar nosso Serviço:** Entender como os usuários interagem com ele, identificar áreas para otimização e desenvolver novos recursos.

<br>

## 3. Como Compartilhamos suas Informações

Nós NÃO vendemos suas informações pessoais. Podemos compartilhar seus dados apenas nas seguintes situações:

- **Prestadores de Serviços:** Podemos compartilhar seus dados com fornecedores e prestadores de serviços terceirizados que realizam serviços em nosso nome, como provedores de hospedagem, mas eles também são obrigados a proteger suas informações e usá-las apenas para os fins para os quais foram divulgadas.
- **Obrigações Legais:** Podemos divulgar seus dados pessoais se formos obrigados por lei ou em resposta a solicitações válidas de autoridades públicas, como um tribunal ou uma agência governamental.
- **Seu Consentimento:** Podemos divulgar suas informações pessoais para qualquer outra finalidade com seu consentimento explícito.

**Nota Importante sobre a Scopus:** Conforme declarado na [Seção 1.3](#13-informações-de-fontes-de-terceiros-dados-da-scopus), os dados aos quais temos acesso não são suas informações pessoais e não compartilhamos nenhuma dessas informações (coletadas pelo Serviço) com a [Elsevier](https://www.elsevier.com) ou a [Scopus](https://www.scopus.com/home.uri).

<br>

## 4. Retenção de Dados

Iremos reter suas informações pessoais apenas pelo tempo necessário para os fins descritos nesta Política de Privacidade e na medida necessária para cumprir nossas obrigações legais (por exemplo, se formos obrigados a reter seus dados para cumprir as leis aplicáveis), resolver disputas, e fazer-se cumprir de nossos acordos e políticas legais.

Por outro lado, normalmente não reteremos nenhuma de suas informações além do arquivo CSV gerado como resultado do levantamento, que permanecerá armazenado no servidor em que o Serviço está sendo executado.

<br>

## 5. Segurança de Dados

A segurança dos seus dados é importante para nós. Implementamos padrões da indústria geralmente aceitos para proteger as informações pessoais que nos são enviadas, tanto durante a transmissão quanto após o recebimento. No entanto, nenhum método de transmissão pela internet ou método de armazenamento eletrônico é 100% seguro. Embora nos esforcemos para usar meios comercialmente aceitáveis para proteger seus dados pessoais, não podemos garantir sua segurança absoluta.

<br>

## 6. Seus Direitos de Dados (Conformidade com a LGPD)

De acordo com a **Lei Geral de Proteção de Dados (LGPD)**, você tem direitos específicos em relação aos seus dados:

- **Acesso:** Solicitar confirmação e detalhes sobre o processamento de dados pessoais.
- **Retificação:** Solicitar a correção de dados incompletos, imprecisos ou desatualizados.
- **Exclusão:** Solicite a exclusão de dados desnecessários, excessivos ou processados ilegalmente.
- **Portabilidade:** Obtenha os dados em um formato estruturado.
- **Revogação do Consentimento:** Revogue seu consentimento a qualquer momento.
- **Informação:** Saiba a finalidade, a duração e as partes envolvidas no processamento de dados.
- **Revisão de Decisões Automatizadas:** Conteste decisões tomadas exclusivamente por algoritmos.
- **Anonimização:** Solicite que os dados sejam anonimizados sempre que possível.
- **Oposição:** Oponha-se ao processamento por motivos legítimos.
- **Reclamação:** Apresente uma reclamação à **Autoridade Nacional de Proteção de Dados (ANPD)**.

<br>

## 7. Atualizações

Reservamo-nos o direito de atualizar estes Termos a qualquer momento. Notificaremos os usuários sobre quaisquer alterações significativas por meio de nosso [repositório do GitHub](https://github.com/mauprogramador/scopus-survey-api) ou [Documentação](https://mauprogramador.github.io/scopus-survey-api/). Seu uso contínuo do Serviço após tais alterações constitui sua aceitação dos novos Termos.

<br>

## 8. Referência

- [**Política de Privacidade da Elsevier**](https://www.elsevier.com/pt-br/legal/privacy-policy)
- [**Políticas de uso da Elsevier**](https://dev.elsevier.com/policy.html)
- [**Lei Geral de Proteção de Dados (LGPD)**](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/lgpd-en-lei-no-13-709-capa.pdf) **`PDF`**
- [**Lei Geral de Proteção de Dados Pessoais (LGPD)**](https://www.gov.br/esporte/pt-br/acesso-a-informacao/lgpd)
- [**Documentação da Scopus Search API**](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)
- [**Documentação da Abstract Retrieval API**](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl)
- [**Configurações da Chave de API**](https://dev.elsevier.com/api_key_settings.html)

<br>

## 9. Contato

Para dúvidas ou preocupações sobre estas Políticas, entre em contato conosco por <sir.silvabmauricio@gmail.com>.
