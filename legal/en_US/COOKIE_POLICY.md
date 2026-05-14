# Cookie Policy

**Scopus Survey API** - _Web API for bibliographic survey of Scopus articles_

> _Last updated: May 13, 2026_

Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul - [IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)<br>
Tecnologia em Análise e Desenvolvimento de Sistemas - [TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/analise-e-desenvolvimento-de-sistemas)<br>

> _Federal Institute of Education, Science and Technology of Mato Grosso do Sul_ <br>
> _Technology in Systems Analysis and Development_

---

This agreement (**"Cookie Policy"**) explains cookies and under what conditions you and the Scopus Survey API (**"Service"**), provided by us (**"we"**, **"us"**, or **"our"**), can manage cookie preferences and usage to improve your experience.

<br>

## 1. What are Cookies?

Cookies[^1][^2] are small files stored on your device (computer, tablet, or mobile phone) when you visit a website. They help the website work more efficiently, provide reporting information, recognize your device, and remember information about your visit, such as your preferences or login information. This is why they are widely used as standard practice on most professional websites. Cookies set by the website owner are called **"first-party"**.

## 2. How We Use Cookies

The only type[^2] of cookies our Service implement and manage is called **"essential"** or **"strictly necessary"**, because they are required for technical reasons as they enable core functionality in order for our Service to operate properly.

We only set and use one **"first-party"**[^2] and **"essential"** Cookie:

- **Token Cookie:** Strictly necessary for authentication and protection against **CSRF** (Cross-Site Request Forgery[^3][^4]). Automatically manage a **CSRF Token**, created using [ItsDangerous's URLSafeTimedSerializer](https://itsdangerous.palletsprojects.com/en/stable/url_safe/)[^5], through HTTP headers and cookies, which is essential for maintaining secure interactions within the Service.

## 3. Cookie Duration

| Cookie       | Type                   | Duration |
| ------------ | ---------------------- | -------- |
| `csrf-token` | Essential / Persistent | 1 hour   |

**Note:** Persistent Cookies[^2] remain on your device for a set period of time or until you delete them.

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

**Note:** Check the details and updates in the [legal information file](../LEGAL.md).

<br>

---

For questions or concerns about these Policies, please contact us at <sir.silvabmauricio@gmail.com>.

References

[^1]: MDN Contributors \(2025). **MDN Web Docs**. [_Using HTTP cookies_ ↗](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)

[^2]: Cloudflare \(©2026). **Cloudflare Learning**. [_What are cookies?_ ↗](https://www.cloudflare.com/learning/privacy/what-are-cookies/)

[^3]: MDN Contributors \(2026). **MDN Web Docs**. [_Cross-site request forgery (CSRF)_ ↗](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF)

[^4]: Cloudflare \(©2026). **Cloudflare Security**. [_What is cross-site request forgery?_ ↗](https://www.cloudflare.com/learning/security/threats/cross-site-request-forgery/)

[^5]: Pallets. \(©2011). **ItsDangerous Documentation**. [_URL Safe Serialization_ ↗](https://itsdangerous.palletsprojects.com/en/stable/url_safe/)
