# Privacy Policy

**Scopus Survey API** - _Web API for bibliographic survey of Scopus articles_

> _Last updated: May 13, 2026_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br>

> _Federal Institute of Education, Science and Technology of Mato Grosso do Sul_ <br>
> _Technology in Systems Analysis and Development_

Data provided by [Scopus](https://www.scopus.com)®. © [Elsevier](https://www.elsevier.com). All rights reserved.

---

This agreement (**"Privacy Policy"**) defines the conditions under which the Scopus Survey API (**"Service"**), provided by us (**"we"**, **"us"**, or **"our"**) collects and uses your information.

<br>

## 1. Information We Collect

### 1.1. Information You Provide to Us

- Your Scopus **API Key**[^1].
- All parameters you submit in the web form.
- If you contact us directly (e.g. via email), we collect the content of your communication and your contact information.

### 1.2. Information Collected Automatically

When you access and use the Service, we automatically collect certain information that your browser or device sends, including:

- **Usage Data:** This may include your IP address, browser info, the pages of our Service that you visit, the time and date of your visit, the time spent on those pages, and other diagnostic data.
- **Token Cookie:** This is strictly necessary for authentication and protection against **CSRF** (Cross-Site Request Forgery[^2][^3]) attacks. Your **CSRF Token** is automatically managed through HTTP headers and cookies, and is essential for maintaining secure interactions within the Service.
- **Tracking Technologies:** Since we use [Slowapi's Limiter](https://slowapi.readthedocs.io/en/latest/)[^4] to control the Service rate limit, it will obtain and store your IP address by default.

### 1.3. Information from Third-Party Sources (Scopus Data)

Our Service queries and accesses the Scopus® database through the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl)[^5] and [Scopus Abstract Retrieval API](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl)[^6]. However, what is retrieved primarily consists of academic publication information[^7], such as article titles, abstracts, author details, citations, and keywords, which are public or academically licensed content[^8].

We would like to clarify that **we do not collect or process any user information from the Scopus APIs, nor do we process any of your account information**[^9]. The only Scopus data we use is your **API Key**, which is not directly linked to your personal information, nor does it allow us to access it.

The Service only uses your **API Key**[^1] to systematically retrieve, validate, and filter the survey data for you, and return it in an organized manner.

<br>

## 2. How We Use Your Information

- **Provide and Maintain our Service:** Ensuring its proper functioning and compliance with its intended purpose.
- **Security and Fraud Prevention:** Managing **CSRF Tokens**, detecting and preventing unauthorized access or malicious activity.
- **Improve our Service:** Understanding how users interact with it, identifying areas for optimization, and developing new features.

<br>

## 3. How We Share Your Information

We DO NOT sell your personal information. We may share it only in the following situations:

- **Service Providers:** We may share your data with third-party vendors and service providers who perform services on our behalf, such as hosting providers, but they are also obligated to protect your information and use it only for the purposes for which it was disclosed.
- **Legal Reasons:** We may disclose your personal data if required to do so by law or in response to valid requests by public authorities, such as a court or a government agency.
- **Your Consent:** We may disclose your personal information for any other purpose with your explicit consent.

**Important Note About Scopus:** As stated in [Section 1.3](#13-information-from-third-party-sources-scopus-data), the data we access is not your personal information, and we do not share any of it (collected by the Service) with [Elsevier](https://www.elsevier.com) or [Scopus](https://www.scopus.com/home.uri).

<br>

## 4. Data Retention

We will retain your personal information only for as long as necessary for the purposes set out in this Privacy Policy and to the extent necessary to comply with our legal obligations (for example, if we are required to retain your data to comply with applicable laws), resolve disputes, and enforce our legal agreements and policies.

On the other hand, we will typically not retain any of your information beyond the CSV file generated as a result of the survey[^8], which will remain stored on the server on which the Service is running.

<br>

## 5. Data Security

The security of your data is important to us. We implement generally accepted industry standards to protect the personal information submitted to us, both during transmission and once we receive it. However, no method of transmission over the internet, or method of electronic storage, is 100% secure. While we strive to use commercially acceptable means to protect your personal data, we cannot guarantee its absolute security.

<br>

## 6. Your Data Rights (LGPD Compliance)

Under the **Brazilian General Data Protection Law (LGPD)**[^10][^11], you have specific rights regarding your data:

- **Access:** Request confirmation and details on personal data processing.
- **Correction:** Request the correction of incomplete, inaccurate, or outdated data.
- **Deletion:** Request the deletion of unnecessary, excessive, or unlawfully processed data.
- **Portability:** Obtain data in a structured format.
- **Revoke Consent:** Revoke your consent at any time.
- **Information:** Know the purpose, duration, and parties involved in data processing.
- **Review Automated Decisions:** Challenge decisions made solely by algorithms.
- **Anonymization:** Request data to be anonymized where possible.
- **Opposition:** Object to processing for legitimate reasons.
- **Complain:** Lodge a complaint with the **National Data Protection Authority (ANPD)**.

<br>

## 7. Updates

We reserve the right to update these Terms at any time. We will notify users of any significant changes via our [GitHub repository](https://github.com/mauprogramador/scopus-survey-api) or [Documentation](https://mauprogramador.github.io/scopus-survey-api/). Your continued use of the Service after such changes constitutes your acceptance of the new Terms.

**Note:** Check the details and updates in the [legal information file](../LEGAL.md)

<br>

---

For questions or concerns about these Policies, please contact us at <sir.silvabmauricio@gmail.com>.

References

[^1]: Elsevier \(©2026). [_"How much data can I retrieve with my APIKey?"_ ↗](https://dev.elsevier.com/api_key_settings.html). **Elsevier Developer Portal**.

[^2]: MDN Contributors \(2026). [_"Cross-site request forgery (CSRF)"_ ↗](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF). **MDN Web Docs**.

[^3]: Cloudflare \(©2026). [_"What is cross-site request forgery?"_ ↗](https://www.cloudflare.com/learning/security/threats/cross-site-request-forgery/). **Cloudflare Security**.

[^4]: Savaete, L. \(2024). [_"API Reference: Limiter"_ ↗](https://slowapi.readthedocs.io/en/latest/api/). **SlowAPI Documentation**.

[^5]: Elsevier \(©2024). [_"Scopus Search API"_ ↗](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl). **Elsevier Developer Portal**.

[^6]: Elsevier \(©2024). [_"Abstract Retrieval API"_ ↗](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl). **Elsevier Developer Portal**.

[^7]: Elsevier \(©2026). [_"Use Policies"_ ↗](https://dev.elsevier.com/policy.html). **Elsevier Developer Portal**.

[^8]: Elsevier \(©2026). [_"Text and Data Mining"_ ↗](https://dev.elsevier.com/academic_research_scopus.html). **Elsevier Developer Portal**.

[^9]: Elsevier \(2026). [_"Privacy Policy"_ ↗](https://www.elsevier.com/legal/privacy-policy). **Elsevier Legal**.

[^10]: National Data Protection Authority (ANPD) (2025). [_"Brazilian Data Protection Law (LGPD)"_ ↗](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/lgpd-en-lei-no-13-709-capa.pdf). [PDF]. **GOV.BR Portal**.

[^11]: Ministério do Esporte (n.d.). [_"Lei Geral de Proteção de Dados Pessoais (LGPD)"_ ↗](https://www.gov.br/esporte/pt-br/acesso-a-informacao/lgpd). [pt-BR]. **GOV.BR Portal**.
