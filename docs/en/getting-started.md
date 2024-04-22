# Getting Started

## Clone

First you need to clone the project from the GitHub repository:
<https://github.com/mauprogramador/scopus-searcher-api>{:target="\_blank"}

On the Bash Terminal using [Git](https://git-scm.com/){:target="\_blank"}:

```zsh
git clone https://github.com/mauprogramador/scopus-searcher-api.git
```

On Vs Code using [Git Extension](https://git-scm.com/book/en/v2/Appendix-A%3A-Git-in-Other-Environments-Git-in-Visual-Studio-Code){:target="\_blank"}:

- Open the **Command Palette** and press `Ctrl` + `Shift` + `P` or `F1`
- Select the `Git: Clone` command and click on it
- Paste the repository URL: <https://github.com/mauprogramador/scopus-searcher-api.git>{:target="\_blank"}
- Press `Enter` or click on `Clone from URL` and select a directory

!!! note

    Take a look at [Source Control Docs](https://code.visualstudio.com/docs/sourcecontrol/overview){:target="\_blank"}.

## Run

With Python3:

!!! note

    First you need to create the [Environment](./environment.md#development-environment).

```zsh
# Run the App locally
make run
```

With Docker:

```zsh
# Run the App in Docker Container
make docker
```

---

## Interactive Swagger

Once you start the application you can access the [Swagger UI](https://github.com/swagger-api/swagger-ui){:target="\_blank"} by: <http://127.0.0.1:8000>{:target="\_blank"}

![Swagger](../images/swagger.png)

Select the **API Endpoint** `/search-articles` and click on the **Try it out** button.

- Enter your `Api Key` and `Keywords`.
- The `Keywords` must be separated by a comma.
- It is mandatory to fill in the `Api Key` field and at least two `keywords`.
- The `X-Access-Token` header will be setted automatically, you **should not** change it.
- Click on the **Execute** button.

![Swagger Search](../images/swagger-search.png)

If any article is successfully found, it will return a [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="\_blank"} containing all the search information. You can click on the **Download** button to download the file.

![Swagger Success](../images/swagger-success.png)

If no article is found, a message will return informing what went wrong. You should first read and analyze the message and try to understand what caused the error before trying again.

![Swagger Error](../images/swagger-error.png)

## Web Application

Once you start the application you can access the Web Application by: <http://127.0.0.1:8000/scopus-searcher/api>{:target="\_blank"}

![Web](../images/web-en.png)

On the web page, click on the fields and enter your data, making sure they are correct.

- Select your preferred language by clicking on the **Flag** symbol (Support for `en-us` and `pt-br`).
- Enter your `Api Key` and `Keywords` in the respective fields.
- Enter one `Keyword` for each field.
- It is mandatory to fill in the `Api key` field and at least two `Keywords` fields.
- Click on the **Search Articles** button and wait for the search results.

![Web Search](../images/web-search-en.png)

All fields on the web page are configured to verify that the information in each respective field is correct, so you must be aware of the rules and conditions regarding the `Api Key` and the `Keywords` provided in the [requirements section](./requirements.md).

As soon as you start typing in a field, it will automatically give you feedback, so stay tuned:

- Remember that it is mandatory to fill in the `Api Key` field and at least two `Keywords` fields.
- The red color will circe the field and a message will be shown if the data is incorrect.
- The green color will circle the field if the data is correct.

![Web Validation](../images/web-validation-en.png)

If any article is successfully found, a message will return informing you of success and [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="\_blank"} containing all the search information will be automatically downloaded.

![Web Success](../images/web-success.png)

If no article is found, a message will return informing what went wrong. You should first read and analyze the message and try to understand what caused the error before trying again.

![Web Error](../images/web-error.png)

You can also check the request response in the browser's [DevTools](https://developer.chrome.com/docs/devtools?hl=pt-br){:target="\_blank"} inspect.

![Inspect Error](../images/inspect-error.png)

## CSV Table

After **successfully** completing the search processing, in addition to downloading the [CSV file](https://pt.wikipedia.org/wiki/Comma-separated_values){:target="\_blank"}, the **Show Table** button will also be released, and when you click on it you will be redirected to a new page in which a table will display a preview of all the article data found.

![Web Loading](../images/web-loading-en.png)
![Web Table](../images/web-table-en.png)

### Search Example

The table below exemplifies the results of a search. Using **Python** and **Machine Learning** as `Keywords`, a total of **6786** articles were returned from the [Scopus Search API](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl){:target="\_blank"}. To avoid time-consuming processing, we [reduced](./scopus-search-api.md#reducing-the-count) the total to just **14**, there was no [loss due to similarity](./data-survey.md#filtering) and it took around **34,012.64ms**.

![Web Table](../images/csv-table.png)

!!! note

    [Click here](../example.csv){:download="example.csv"} to download the CSV file for the survey example above.
