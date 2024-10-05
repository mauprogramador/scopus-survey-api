# Environment

## Configuration

| **Parameter**  | **Description**                                                                                                | **Default** |
| -------------- | -------------------------------------------------------------------------------------------------------------- | ----------- |
| `debug`        | Enable the debug logs output                                                                                   | `false`     |
| `logging_file` | Enable saving log records to file. This will create a `.logs` folder                                           | `false`     |
| `host`         | Bind the socket to this host address.<br>Set `0.0.0.0` to make the application available on your local network | `127.0.0.1` |
| `port`         | Bind to a socket and run the application with this port                                                        | `8000`      |
| `reload`       | Enables automatic reloading of the application when files are modified                                         | `false`     |

You can configure some parameters for the application in the `pyproject.toml` file, such as:

```toml title="pyproject.toml" linenums="81"
[application]
debug = false
logging_file = false
host = "127.0.0.1"
port = 8000
reload = false
```

You can also set [environment variables](https://en.wikipedia.org/wiki/Environment_variable){:target="\_blank"} to **override the default configuration** when running the application **locally** or in a **Docker container**.

```.env title=".env" linenums="1"
DEBUG=false

LOGGING_FILE=false

HOST=127.0.0.1

PORT=8000

RELOAD=false
```

## Python Environment

It is necessary to prepare an environment with the correct dependencies to work properly with each area of the application. To do this, you need to install [Python3 `v3.11`]({{links.python}}/downloads/release/python-3117/){:target="\_blank"} with [Venv]({{links.pythonDocs}}/venv.html){:target="\_blank"} and [Pip](https://pip.pypa.io/en/stable/installation/){:target="\_blank"}.

!!! info

    This project uses [Poetry](https://python-poetry.org/){:target="\_blank"} to package and manage Python dependencies.

!!! tip

    You can also use [Docker](https://www.docker.com/){:target="\_blank"} to run the application.

### Setup the [Virtual Environment]({{links.pythonDocs}}/venv.html){:target="\_blank"}

```zsh
# Setup Venv
make setup

# Activate Venv
source .venv/bin/activate
```

## Dependencies

### Complete Environment

:material-arrow-down-bold-box: Install **all** dependencies.

=== "with Poetry"

    ```zsh
    (.venv) poetry install
    ```

=== "with Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-all.txt
    ```

### Application Environment

:material-arrow-down-bold-box: Install only the **application** dependencies.

=== "with Poetry"

    ```zsh
    (.venv) make install
    ```

=== "with Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements.txt
    ```

<br>
:material-play-circle: Run the application

=== "Locally"

    ```zsh
    # Run the application Locally
    (.venv) make run
    ```

=== "Docker"

    ```zsh
    # Run the application in Docker Container
    make docker
    ```

### Development Environment

:material-arrow-down-bold-box: Install only the **development** dependencies.

=== "with Poetry"

    ```zsh
    (.venv) poetry install --only dev
    ```

=== "with Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-dev.txt
    ```

<br>
:material-play-circle: Perform [Formatting](https://code.visualstudio.com/docs/python/formatting){:target="\_blank"}, [Linting](https://code.visualstudio.com/docs/python/linting){:target="\_blank"}, and [Vulnerability Auditing](https://en.wikipedia.org/wiki/Code_audit){:target="\_blank"}.

```zsh
# run Formatting
(.venv) make format

# run Linting
(.venv) make lint

# run Linting in Tests
(.venv) make lint-tests

# run Audit Vulnerability
(.venv) make audit
```

### Tests Environment

:material-arrow-down-bold-box: Install only the **tests** dependencies.

=== "with Poetry"

    ```zsh
    (.venv) poetry install --only test
    ```

=== "with Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-test.txt
    ```

<br>
:material-play-circle: Run the tests and check the tests coverage

=== "Locally"

    ```zsh
    # Run Pytest in Venv
    (.venv) make test

    # Run Coverage in Venv
    (.venv) make coverage
    ```

=== "Docker"

    ```zsh
    # Run Pytest in Docker
    make test-docker

    # Run Coverage in Docker
    make coverage-docker
    ```

### Documentation Environment

:material-arrow-down-bold-box: Install only the **documentation** dependencies.

=== "with Poetry"

    ```zsh
    (.venv) poetry install --only docs
    ```

=== "with Pip"

    ```zsh
    (.venv) pip3 install -r requirements/requirements-docs.txt
    ```

<br>
:material-play-circle: Run [Mkdocs](https://www.mkdocs.org/){:target="\_blank"} documentation.

Run Locally and access the web page at <http://127.0.0.1:8000>{:target="\_blank"}.

```zsh
# Serve MkDocs
(.venv) make docs
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
