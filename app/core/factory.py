from app.adapters.gateway.scopus_api import ScopusApi
from app.core.usecase import Scopus


def make_usecase() -> Scopus:
    gateway = ScopusApi()
    usecase = Scopus(gateway)
    return usecase
