from toml import load

from app.core.interfaces import Pyproject


class PyprojectToml:
    FILENAME = 'pyproject.toml'
    ENCODING = 'utf-8'

    def __init__(self) -> None:
        with open(self.FILENAME, encoding=self.ENCODING) as file:
            pyproject = load(file)

        tools: dict[str, dict] = pyproject.get('tool', {})
        poetry: dict[str, str | list[str]] = tools.get('poetry', {})
        self.version = poetry.get('version', '2.0.0')

        application: Pyproject.TomlType = pyproject.get('application', {})
        self.reload: bool = application.get('reload', False)

        self.debug = application.get('debug', False)
        self.logging_file = application.get('logging_file', False)

        host: str = application.get('host', '127.0.0.1')
        self.host = host if isinstance(host, str) else '127.0.0.1'

        port: int = application.get('port', 8000)
        self.port = port if isinstance(port, int) else 8000

    @property
    def uvicorn(self) -> Pyproject.TomlType:
        return {
            'app': 'app.framework.fastapi.main:app',
            'host': self.host,
            'port': self.port,
            'reload': self.reload,
        }

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'
