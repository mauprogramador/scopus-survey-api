# Cookie Policy

**Scopus Survey API** - *Web API for bibliographic survey of Scopus articles*

> *Last updated: August 10, 2025*

Federal Institute of Mato Grosso do Sul - [IFMS - Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br/>
Technology in Systems Analysis and Development - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br/>

---

This agreement (**"Cookie Policy"**) explains cookies and under what conditions you and the Scopus Survey API (**"Service"**), provided by us (**"we"**, **"us"**, or **"our"**), can manage cookie preferences and usage to improve your experience.

<br>

## 1. What are Cookies?

Cookies are small files stored on your device (computer, tablet, or mobile phone) when you visit a website. They help the website work more efficiently, provide reporting information, recognize your device, and remember information about your visit, such as your preferences or login information. This is why they are widely used as standard practice on most professional websites. Cookies set by the website owner are called **"first-party"**.

## 2. How We Use Cookies

The only type of cookies our Service implement and manage is called **"essential"** or **"strictly necessary"**, because they are required for technical reasons as they enable core functionality in order for our Service to operate properly.

We only set and use two **"first-party"** and **"essential"** Cookies:

- **Session Cookie:** Using [Starlette's SessionMiddleware](https://www.starlette.io/middleware/#sessionmiddleware) to add a signed cookie-based HTTP sessions to track and control the **Session** time.
- **Token Cookie:** Strictly necessary for authentication and protection against **CSRF** (Cross-Site Request Forgery). Automatically manage a **CSRF Token**, created using [ItsDangerous's URLSafeTimedSerializer](https://itsdangerous.palletsprojects.com/en/stable/url_safe/), through headers, cookies, query parameters, and session, and is essential for maintaining secure interactions within the Service.

## 3. Cookie Duration

- **Session Cookies**: Temporary and expire when you close your browser.
- **Persistent Cookies**: Remain on your device for a set period of time or until you delete them.

| Cookie       | Type                       | Duration        |
|--------------|----------------------------|-----------------|
| `session`    | **Essential / Session**    | Browser session |
| `csrf-token` | **Essential / Persistent** | **1 hour**      |

## 4. How can I Control Cookies?

Our essential Cookies **CANNOT BE REJECTED** as they are strictly necessary to the Service.

You have control over how cookies are managed on your device, preventing them to setting by adjusting your browser settings to accept or reject cookies, or to alert you when a cookie is being placed. Be aware that disabling our cookies will affect the functionality of the Service, resulting it to not work as intended.

**Browser Settings:** you can usually find these settings in the **"Options"** or **"Preferences"** menu of your browser. For more information, visit the support page for your browser:

- **Chrome:** [Delete, allow and manage cookies in Chrome](https://support.google.com/chrome/answer/95647).
- **Firefox:** [Enhanced Tracking Protection in Firefox for desktop](https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop?redirectslug=enable-and-disable-cookies-website-preferences&redirectlocale=en-US).
- **Safari:** [Clear cookies in Safari on Mac](https://support.apple.com/en-ie/guide/safari/sfri11471/18.0/mac/15.0).
- **Edge:** [Manage cookies in Microsoft Edge](https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09).
- **Opera:** [Manage cookies in pages](https://help.opera.com/en/latest/web-preferences/#cookies).
- **Brave:** [How Do I Clear Cookies And Site Data In Brave?](https://support.brave.app/hc/en-us/articles/360048833872-How-Do-I-Clear-Cookies-And-Site-Data-In-Brave).

## 5. Updates

We may update this Cookie Policy from time to time to reflect changes in legal requirements or our use of cookies. We will notify users of any significant changes via our [GitHub repository](https://github.com/mauprogramador/scopus-survey-api) or [Documentation](https://mauprogramador.github.io/scopus-survey-api/). Your continued use of the Service after such changes constitutes your acceptance of the new Terms.

## 6. Reference

- **MDN web docs:** [Cookies HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Guides/Cookies).
- **Cloudflare:** [What are cookies?](https://www.cloudflare.com/learning/privacy/what-are-cookies/).
- **Starlette:** [SessionMiddleware](https://www.starlette.io/middleware/#sessionmiddleware).
- **ItsDangerous:** [URLSafeTimedSerializer](https://itsdangerous.palletsprojects.com/en/stable/url_safe/).
- **MDN web docs:** [Cross-site request forgery (CSRF)](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF).
- **Cloudflare:** [What is cross-site request forgery?](https://www.cloudflare.com/learning/security/threats/cross-site-request-forgery/).

## 7. Contact

For questions or concerns about these Policies, please contact us at <sir.silvabmauricio@gmail.com>.
