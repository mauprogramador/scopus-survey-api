# Translation Guide

**Scopus Survey API** - *Web API for bibliographic survey of Scopus articles*

> *Last updated: August 10, 2025*

Federal Institute of Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Technology in Systems Analysis and Development - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

---

Typically, programs and websites are written and documented in English, as we use it as a common global communication standard, making it very practical for development environments for users from all countries.

On the other hand, considering accessibility, most people feel less comfortable with English than with their native language and prefer to use their native language whenever possible.

Therefore, the fact that this web API is a **Brazilian project** owned by an **educational institution** means we need at least two languages available: **English** and **Português**.

<br>

## 1. About gettext

To perform the translations, we first write all the text data to [Portable Object (PO)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) format files. We then use the [GNU msgfmt](https://www.gnu.org/software/gettext/manual/html_node/msgfmt-Invocation.html) program to generate a binary message catalog from a textual translation description, resulting in [Machine Object (MO)](ttps://www.gnu.org/software/gettext/manual/html_node/MO-Files.html) format files.

We then use [Python's gettext module](https://docs.python.org/3/library/gettext.html), which provides internationalization and localization, to **load all these MO binary data files and store the translations in a global cache** for later use in building **Jinja templates** and **JSON responses**.

<br>

## 2. Prefix Convention

| Prefix | Category        | Example `msgid` | Scope                                 |
|--------|-----------------|-----------------|---------------------------------------|
| `T`    | General text    | `T0709`         | Headings, Paragraphs, Divs            |
| `E`    | Errors          | `E0709`         | Validation, API Errors, Exceptions    |
| `F`    | Form items      | `F0709`         | Labels, Placeholders, Fields, Buttons |
| `M`    | Messages        | `M0709`         | Alerts, Modals                        |
| `H`    | Help text       | `H0709`         | Instructions, Labels, Feedbacks       |
| `I`    | Icons / Images  | `I0709`         | Aria-labels, Descriptions             |

<br>

## 3. Compilation

- **Locale Root Directory:** `web/locales/`.
- **Languages Currently Supported:** English (`en-US`) and Português (`pt-BR`).

```bash
# Compile .po to .mo
msgfmt web/locales/en_US/LC_MESSAGES/file.po -o web/locales/en_US/LC_MESSAGES/file.mo
```

<br>

## 4. Reference

- **Python Docs:** [gettext - Multilingual internationalization services](https://docs.python.org/3/library/gettext.html).
- **GNU:** [msgfmt Invocation (GNU gettext utilities)](https://www.gnu.org/software/gettext/manual/html_node/msgfmt-Invocation.html).
- **GNU:** [gettext - GNU Project - Free Software Foundation](https://www.gnu.org/software/gettext/
).
- **GNU:** [The Format of GNU PO Files (GNU gettext utilities)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).
- **GNU:** [The Format of GNU MO Files (GNU gettext utilities)](https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html).
- **Wikipedia:** [Internationalization and localization](https://en.wikipedia.org/wiki/Internationalization_and_localization).
- **WC3:** [About W3C Internationalization (i18n)](https://www.w3.org/International/i18n-drafts/nav/about).

<br>

## 5. Contact

For questions or concerns about Translation, please contact us at <sir.silvabmauricio@gmail.com>.
