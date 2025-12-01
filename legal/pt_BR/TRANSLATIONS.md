# Traduções

**Scopus Survey API** - _API da Web para levantamento bibliográfico de artigos da Scopus_

> _Última atualização: 30 de Novembro de 2025_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

> **Nota:** Esta tradução é fornecida apenas para conveniência e acessibilidade, prevalecendo a [versão em inglês](./../en_US/TRANSLATIONS.md) deste documento, para a qual você deve recorrer em caso de discrepâncias.

---

Normalmente, os programas e sites são escritos e documentados em Inglês, pois o usamos como padrão de comunicação global comum, tornando-o muito prático para ambientes de desenvolvimento para usuários de todos os países.

Por outro lado, considerando a acessibilidade, a maioria das pessoas se sente menos confortável com o inglês do que com sua língua nativa e prefere usá-la sempre que possível.

Portanto, o fato desta API da web ser um **projeto brasileiro** pertencente a uma **instituição de ensino** significa que precisamos de pelo menos dois idiomas disponíveis: **Inglês** e **Português**.

<br>

## 1. Sobre o `gettext`

Para realizar as traduções, primeiro escrevemos todos os dados de texto em arquivos no formato [Portable Object (PO)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html). Em seguida, utilizamos o programa [GNU msgfmt](https://www.gnu.org/software/gettext/manual/html_node/msgfmt-Invocation.html) para gerar um catálogo binário de mensagens a partir de uma descrição textual de tradução, resultando em arquivos no formato [Machine Objeto (MO)](https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html).

Utilizamos então o [módulo gettext do Python](https://docs.python.org/pt-br/3/library/gettext.html), que fornece internacionalização e localização, para **carregar todos esses arquivos de dados binários MO e armazenar as traduções em um cache global** para uso posterior na construção dos **templates Jinja** e **respostas JSON**.

<br>

## 2. Convenção de Prefixo

| Prefixo | Categoria           | Exemplo `msgid` | Escopo                                  |
| ------- | ------------------- | --------------- | --------------------------------------- |
| `T`     | Texto Geral         | `T0709`         | Títulos, Parágrafos, Divs               |
| `E`     | Erros               | `E0709`         | Validação, Erros de API, Exceções       |
| `F`     | Itens de Formulário | `F0709`         | Rótulos, _Placeholders_, Campos, Botões |
| `M`     | Mensagens           | `M0709`         | Alertas, Modais                         |
| `H`     | Texto de Ajuda      | `H0709`         | Instruções, Rótulos, _Feedbacks_        |
| `I`     | Ícones / Imagens    | `I0709`         | Rótulos Aria, Descrições                |
| `A`     | Abreviações         | `A0709`         | Título dos elementos abreviados         |

<br>

## 3. Compilação

- **Diretório Raiz das Traduções:** `web/locales/`.
- **Idiomas Atualmente Suportados:** Inglês (`en-US`) e Português (`pt-BR`).

```bash
# Compilar .po para .mo
msgfmt web/locales/en_US/LC_MESSAGES/file.po -o web/locales/en_US/LC_MESSAGES/file.mo
```

<br>

## 4. Referências

- **Documentação do Python:** [gettext - Serviços de internacionalização multilíngues](https://docs.python.org/pt-br/3/library/gettext.html).
- **GNU:** [Executando o msgfmt (utilitários gettext do GNU)](https://www.gnu.org/software/gettext/manual/html_node/msgfmt-Invocation.html).
- **GNU:** [gettext - Projeto GNU - Fundação para o Software Livre](https://www.gnu.org/software/gettext/).
- **GNU:** [O formato dos arquivos PO do GNU (utilitários gettext do GNU)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).
- **GNU:** [O formato dos arquivos MO do GNU (utilitários gettext do GNU)](https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html).
- **Wikipedia:** [Internacionalização e localização](https://pt.wikipedia.org/wiki/Internacionaliza%C3%A7%C3%A3o_e_tradu%C3%A7%C3%A3o).
- **WC3:** [Sobre a Internacionalização (i18n) do W3C](https://www.w3.org/International/i18n-drafts/nav/about).

<br>

## 5. Contato

Para dúvidas ou preocupações sobre a Tradução, entre em contato conosco por <sir.silvabmauricio@gmail.com>.
