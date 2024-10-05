# Hooks and Actions

When developing an application, it's common to use different technologies to ensure the good condition of the code and its functioning. To do this, we can use verification and integration tools when certain important actions occur in code {{abbr.versioning}}.

## Git Hooks

Below is the {{abbr.clientSide}} [Git Hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks){:target="\_blank"} script used in this application, it is called `pre-commit` because it is the first that will be automatically run locally when a {{abbr.commit}} occurs, and will perform certain checking actions depending on the files that have been changed and are being committed.

- Run the {{abbr.lint}} when files from the `app` folder are committed.
- Run the {{abbr.lint}} when files from the `tests` folder are committed.
- Run the **Vulnerability Audit** when files from the `requirements` folder are committed, which means new libraries, packages or dependencies have been installed.
- Run the **Tests** anyway, ensuring everything is working.

```sh title="pre-commit" linenums="1"
#!/bin/bash

make format

if git diff --cached --name-only | grep -q '^app/'; then
  make lint
fi

if git diff --cached --name-only | grep -q '^tests/'; then
  make lint-tests
fi

if git diff --cached --name-only | grep -q '^requirements/'; then
  make audit
fi

make test
```

!!! tip

    Don't forget to grant the necessary permissions to the hook file.
    ```zsh
    chmod +x .git/hooks/pre-commit
    ```

## GitHub Actions

On the {{abbr.serverSide}}, this application uses [GitHub Actions](https://github.com/features/actions){:target="\_blank"} to create {{abbr.workflows}} that will automatically trigger when a `push` event occurs to the remote [GitHub](https://github.com/){:target="\_blank"} repository, automating verification and deployment jobs to run automatically.

### [Verification Job :octicons-link-external-16:]({{links.workflows}}/verification.yml){:target="\_blank"}

For **{{abbr.linting}} and Testing**, it will check the repository, configure [Python3]({{links.python}}){:target="\_blank"}, install [Poetry](https://python-poetry.org/){:target="\_blank"}, load cached {{abbr.venv}}, and install all necessary dependencies like [Pytest](https://docs.pytest.org/en/8.0.x/contents.html){:target="\_blank"} and [Pylint](https://pylint.readthedocs.io/en/stable/){:target="\_blank"} to perform lint and test operations on the code ensuring everything is fine.

### [Documentation Job :octicons-link-external-16:]({{links.workflows}}/documentation.yml){:target="\_blank"}

It will check the repository, configure [Python3]({{links.python}}){:target="\_blank"}, load cached {{abbr.venv}}, and install the [MkDocs](https://www.mkdocs.org/){:target="\_blank"} and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"} libraries to configure, {{abbr.deploy}} and [publish](https://squidfunk.github.io/mkdocs-material/publishing-your-site/){:target="\_blank"} the static application documentation web page, written in [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax){:target="\_blank"}, and which will be hosted on [GitHub Pages](https://pages.github.com/){:target="\_blank"} on [GitHub's](https://github.com/){:target="\_blank"} `github.io` domain.
