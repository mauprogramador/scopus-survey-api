# Hooks and Actions

When developing an application, it's common to use different technologies to ensure the good condition of the code and its functioning. To do this, we can use tools for checking and integration when certain important actions occur in code versioning.

## Git Hooks

Below is the **client-side** [Git Hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks){:target="\_blank"} script used in this **API**, it is called `pre-commit` because it is the first that will be automatically run locally when a commit occurs, and will perform certain checking actions depending on the files that have been changed and are being committed.

- Run **Lint** when files from the `app` folder are committed.
- Run **Lint** when files from the `tests` folder are committed.
- Run **Vulnerability Audit** when files from the `requirements` folder are committed, which means new libraries, packages or dependencies have been installed.
- Run the **Tests** anyway, ensuring everything is working.

```sh title="pre-commit"
#!/bin/bash

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

## GitHub Actions

On the **server-side**, this **API** uses [GitHub Actions](https://github.com/features/actions){:target="\_blank"} to create **workflows** that will automatically trigger when a `push` event occurs to the remote [GitHub](https://github.com/){:target="\_blank"} repository, automating verification and deployment jobs to run automatically.

### Verification Job

For **Linting and Testing**, it will check the repository, configure [Python](https://www.python.org/){:target="\_blank"}, install [Poetry](https://python-poetry.org/){:target="\_blank"}, load cached [Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install all necessary dependencies like [Pytest](https://docs.pytest.org/en/8.0.x/contents.html){:target="\_blank"} and [Pylint](https://pylint.readthedocs.io/en/stable/){:target="\_blank"} to perform lint and test operations on the code ensuring everything is fine.

### Documentation Job

To **deploy and publish** the **API** documentation, it will check the repository, configure [Python](https://www.python.org/){:target="\_blank"}, load cached [Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install the necessary dependencies like [MkDocs-Material](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"} to perform deploy and publish operations using [MkDocs](https://www.mkdocs.org/){:target="\_blank"}.

We use the [MkDocs](https://www.mkdocs.org/){:target="\_blank"} and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"} libraries to configure, deploy and [publish](https://squidfunk.github.io/mkdocs-material/publishing-your-site/){:target="\_blank"} the static documentation website, written in [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax){:target="\_blank"}, and which will be hosted on [GitHub Pages](https://pages.github.com/){:target="\_blank"} on [GitHub's](https://github.com/){:target="\_blank"} `github.io` domain.
