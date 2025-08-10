# Privacy Policy

**Scopus Survey API** - *Web API for bibliographic survey of Scopus articles*

> *Last updated: August 10, 2025*

Federal Institute of Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Technology in Systems Analysis and Development - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

Data provided by **Scopus® (Elsevier)**.

---

This agreement (**"Privacy Policy"**) defines the conditions under which the Scopus Survey API (**"Service"**), provided by us (**"we"**, **"us"**, or **"our"**) collects and uses your information.

<br>

## 1. Information We Collect

### 1.1. Information You Provide to Us

- Your Scopus **API Key**.
- All parameters you submit in the web form.
- If you contact us directly (e.g. via email), we collect the content of your communication and your contact information.

### 1.2. Information Collected Automatically

When you access and use the Service, we automatically collect certain information that your browser or device sends, including:

- **Usage Data:** This may include your IP address, browser info, the pages of our Service that you visit, the time and date of your visit, the time spent on those pages, and other diagnostic data.
- **Session Cookie:** We use [Starlette's SessionMiddleware](https://www.starlette.io/middleware/#sessionmiddleware) to add a signed cookie-based HTTP sessions to track and control the **Session** time.
- **Token Cookie:** This is strictly necessary for authentication and protection against **CSRF** (Cross-Site Request Forgery). Your **CSRF Token**, is automatically managed through headers, cookies, query parameters, and session, and is essential for maintaining secure interactions within the Service.
- **Tracking Technologies:** Since we use [Slowapi's Limiter](https://slowapi.readthedocs.io/en/latest/) to control the Service rate limit, it will obtain and store your IP address by default.

### 1.3. Information from Third-Party Sources (Scopus Data)

Our Service queries and accesses the Scopus® database through the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl) and [Scopus Abstract Retrieval API](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl). However, what is retrieved primarily consists of academic publication information, such as article titles, abstracts, author details, citations, and keywords, which are public or academically licensed content.

We would like to clarify that **we do not collect or process any user information from the Scopus APIs, nor do we process any of your account information**. The only Scopus data we use is your **API Key**, which is not directly linked to your personal information, nor does it allow us to access it.

The Service only uses your **API Key** to systematically retrieve, validate, and filter the survey data for you, and return it in an organized manner.

<br>

## 2. How We Use Your Information

- **Provide and Maintain our Service:** Ensuring its proper functioning and compliance with its intended purpose.
- **Security and Fraud Prevention:** Managing **Session and CSRF Tokens**, detecting and preventing unauthorized access or malicious activity.
- **Improve our Service:** Understanding how users interact with it, identifying areas for optimization, and developing new features.

<br>

## 3. How We Share Your Information

We do not sell your personal information. We may share it only in the following situations:

- **Service Providers:** We may share your data with third-party vendors and service providers who perform services on our behalf, such as hosting providers, but they are also obligated to protect your information and use it only for the purposes for which it was disclosed.
- **Legal Reasons:** We may disclose your personal data if required to do so by law or in response to valid requests by public authorities, such as a court or a government agency.
- **Your Consent:** We may disclose your personal information for any other purpose with your explicit consent.

**Important Note About Scopus:** As stated in [Section 1.3](#13-information-from-third-party-sources-scopus-data), the data we access is not your personal information, and we do not share any of it (collected by the Service) with [Elsevier](https://www.elsevier.com) or [Scopus](https://www.scopus.com/home.uri).

<br>

## 4. Data Retention

We will retain your personal information only for as long as necessary for the purposes set out in this Privacy Policy and to the extent necessary to comply with our legal obligations (for example, if we are required to retain your data to comply with applicable laws), resolve disputes, and enforce our legal agreements and policies.

On the other hand, we will typically not retain any of your information beyond the CSV file generated as a result of the survey, which will remain stored on the server on which the Service is running.

<br>

## 5. Data Security

The security of your data is important to us. We implement generally accepted industry standards to protect the personal information submitted to us, both during transmission and once we receive it. However, no method of transmission over the internet, or method of electronic storage, is 100% secure. While we strive to use commercially acceptable means to protect your personal data, we cannot guarantee its absolute security.

<br>

## 6. Your Data Rights (LGPD Compliance)

Under the **Brazilian General Data Protection Law (LGPD)**, you have specific rights regarding your data:

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

## 7. Changes

We reserve the right to update these Terms at any time. We will notify users of any significant changes via our [GitHub repository](https://github.com/mauprogramador/scopus-survey-api) or [Documentation](https://mauprogramador.github.io/scopus-survey-api/). Your continued use of the Service after such changes constitutes your acceptance of the new Terms.

<br>

## 8. Reference links

- [**Elsevier Privacy Policy**](https://www.elsevier.com/legal/privacy-policy)

- [**Elsevier Use Policies**](https://dev.elsevier.com/policy.html)

- [**Brazilian Data Protection Law (LGPD)**](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/lgpd-en-lei-no-13-709-capa.pdf)

- **`pt-BR`** [**Lei Geral de Proteção de Dados Pessoais (LGPD)**](https://www.gov.br/esporte/pt-br/acesso-a-informacao/lgpd)

- [**Scopus Search API Documentation**](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)

- [**Abstract Retrieval API Documentation**](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl)

- [**API Key Settings**](https://dev.elsevier.com/api_key_settings.html)

<br>

## 9. Contact

For questions or concerns about these Policies, please contact us at <sir.silvabmauricio@gmail.com>.
