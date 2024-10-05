# Tests

## Automated Tests

**:material-test-tube: Unitary:** tests the individual components (each unit) in isolation.<br>

**:material-test-tube: Integration:** tests the combined entity of different units, modules or components.<br>

**:material-shield-check: Coverage:** test coverage of **99%**.

```text
.
├── tests
│   ├── helpers/
│   ├── integration/
│   |   ├── adapters/
|   |   |   ├── gateway/
|   |   |   └── helpers/
│   |   ├── core/
|   |   |   └── usecases/
│   |   └── framework/
|   |       ├── dependencies/
|   |       ├── exceptions/
|   |       ├── fastapi/
|   |       └── middleware/
│   ├── mocks/
│   └── unitary/
│       ├── adapters/
|       |   ├── gateway/
|       |   ├── helpers/
|       |   └── presenters/
│       ├── core/
|       |   ├── data/
|       |   ├── domain/
|       |   └── usecases/
│       └── framework/
|           ├── dependencies/
|           └── exceptions/
```

You can configure and use the [VsCode to test](https://code.visualstudio.com/docs/python/testing){:target="\_blank"} all the scripts with [Pytest](https://docs.pytest.org/en/8.0.x/){:target="\_blank"} and [Coverage](https://coverage.readthedocs.io/en/7.4.3/){:target="\_blank"}:

```json title="launch.json" linenums="1"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "app.framework.fastapi.main",
      "pythonArgs": ["-Xfrozen_modules=off"],
      "jinja": true,
      "console": "integratedTerminal",
    }
  ]
}
```

=== "Locally with Poetry"

    ```zsh
    # Setup Venv
    make setup

    # Activate Venv
    source .venv/bin/activate

    # Install test dependencies with Poetry
    (.venv) poetry install --only test

    # Run Pytest in Venv
    (.venv) make test

    # Run Coverage in Venv
    (.venv) make coverage
    ```

=== "Locally with Pip"

    ```zsh
    # Setup Venv
    make setup

    # Activate Venv
    source .venv/bin/activate

    # Install test dependencies with Pip
    (.venv) pip3 install -r requirements/requirements-test.txt

    # Run Pytest in Venv
    (.venv) make test

    # Run Coverage in Venv
    (.venv) make coverage
    ```

=== "Docker"

    ```zsh
    # Run the App in Docker Container
    make docker

    # Run Pytest in Docker
    make test-docker

    # Run Coverage in Docker
    make coverage-docker
    ```

![Pytest](../assets/img/pytest.png "Pytest")

## Scopus APIs Request Tests

Install the [REST Client VsCode Extension](https://github.com/Huachao/vscode-restclient){:target="\_blank"} to configure and send requests to **Scopus APIs** for testing.

![REST Client](../assets/img/rest-client.png "REST Client")

**1.** Access the `client.http` file.<br>
**2.** Insert your `API Key` in `@apikey =`.<br>
**3.** Click on `Send Request`.

![Client File](../assets/img/client-http.png "Client File")
