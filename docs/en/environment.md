# Environment

It is necessary to prepare an environment with the correct dependencies to work properly with each area of the application. To do this, you need to install [Python v3.11](https://www.python.org/downloads/release/python-3117/){:target="\_blank"} with [Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"} and [Pip](https://pip.pypa.io/en/stable/installation/){:target="\_blank"}, or install [Docker](https://www.docker.com/){:target="\_blank"}.

## Development Environment

Create the [Python Virtual Environment - Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install **all** necessary dependencies.

### Poetry

```zsh
# Create Venv
make venv

# Activate Venv
source .venv/bin/activate

# Install all dependencies
(.venv) make install
```

### Pip

```zsh
# Create Venv
make venv

# Activate Venv
source .venv/bin/activate

# Install all dependencies
(.venv) pip3 install -r requirements/requirements-all.txt
```

!!! note

    **After installing the dependencies you can [Get Started](./getting-started.md).**

### Formatting, Linting and Audit Vulnerability

```zsh
# Run Formatting
(.venv) make format

# Run Linting
(.venv) make lint

# Run Linting in Tests
(.venv) make lint-tests

# Run Audit Vulnerability
(.venv) make audit
```

## Application Environment

Create the [Python Virtual Environment - Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install only the **application** dependencies.

```zsh
# Create Venv
make venv

# Activate Venv
source .venv/bin/activate

# Install application dependencies
(.venv) pip3 install -r requirements/requirements.txt
```

## Tests Environment

Create the [Python Virtual Environment - Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install only the **tests** dependencies.

```zsh
# Create Venv
make venv

# Activate Venv
source .venv/bin/activate

# Install tests dependencies
(.venv) pip3 install -r requirements/requirements-test.txt
```

## Documentation Environment

Create the [Python Virtual Environment - Venv](https://docs.python.org/3/library/venv.html){:target="\_blank"}, and install only the **documentation** dependencies.

```zsh
# Create Venv
make venv

# Activate Venv
source .venv/bin/activate

# Install documentation dependencies
(.venv) pip3 install -r requirements/requirements-docs.txt
```

### Run [Mkdocs](https://www.mkdocs.org/){:target="\_blank"} documentation

Run locally and access the web page: <http://127.0.0.1:8000>{:target="\_blank"}

```zsh
# Serve MkDocs in Venv
(.venv) make docs
```

Run in Docker and access the web page: <http://127.0.0.1:8001>{:target="\_blank"}

```zsh
# Serve MkDocs in Docker
make docker-docs
```

## Requirements Files

You can generate multiple [requirements files](https://pip.pypa.io/en/stable/reference/requirements-file-format/){:target="\_blank"} for different purposes.

```zsh
# Requirements only for the Application dependencies
(.venv) make req

# Requirements for the Application with Development dependencies
(.venv) make req-dev

# Requirements for the Documentation dependencies
(.venv) make req-docs

# Requirements for the Tests dependencies
(.venv) make req-test

# Requirements for All dependencies
(.venv) make req-all
```
