# Requirements

## API Key

You must obtain an `Api Key` to use the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="_blank"} and search for articles. This key has no spaces and is made up of 32 characters containing only letters and numbers. It can be obtained by accessing the [Elsevier Developer Portal](https://dev.elsevier.com/){:target="_blank"}, clicking on the **I want an API Key** button and registering.

![Elsevier Portal](../images/elsevier-portal.png)

If you are part of an educational institution, you can try to confirm if your institution is registered with [Elsevier](https://www.elsevier.com/pt-br){:target="_blank"} to sign in via your organization, or you can also try to register with your academic email.

## Keywords

Based on the theme or subject of your research, you must select a minimum of two and a maximum of four `keywords`, which will be used as parameters and filters when searching for articles in the API. They will be searched simultaneously in the title, abstract and keywords of the articles. Each `keyword` must be written in English, containing only letters, numbers, spaces and underscores, with a minimum of 2 and a maximum of 20 characters.
