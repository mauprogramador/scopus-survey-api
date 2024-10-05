# Requirements

## API Key

You must obtain an `API Key` to access the [Scopus {{abbr.api}}s]({{links.scApis}}){:target="\_blank"} to search and retrieve the articles' information. It **has no spaces** and is **made up of 32 characters** containing **only letters and numbers**. It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/){:target="\_blank"}, clicking on the **I want an API Key** button and registering.

![Elsevier Portal](../assets/img/elsevier-portal.png "Elsevier Portal")

If you are part of an educational institution, you can try to confirm if your institution is registered with [Elsevier]({{links.elsevier}}){:target="\_blank"} to sign in via your organization, or you can also try to register with your academic email.

## Keywords

Based on the theme or subject of your research, you must select a **minimum of two** and a **maximum of four `keywords`**, which will be used as parameters and filters in the simultaneous search in the title, abstract and keywords of the articles. Each `keyword` must be **written in English**, containing **only letters, numbers, spaces and underscores**, with a **minimum of 2** and a **maximum of 50 characters**.

Example

```text
Computer Vision, Scopus, Machine Learning, Bibliometric
```

## Institutional Network

Please be aware that the `API Key` will only authenticate correctly if you submit it while inside your **university/institution's network**, and this does not include {{abbr.vpn}} or {{abbr.proxy}} access. Therefore, if you are **fully remote** and **off-campus**, the **abstract** and **all authors** of the articles will **not be returned**.
