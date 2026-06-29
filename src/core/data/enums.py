from enum import StrEnum, auto, unique


@unique
class Lang(StrEnum):
    EN_US = "en-US"
    PT_BR = "pt-BR"

    @property
    def locale(self) -> str:
        return self.value.replace("-", "_")


@unique
class ExcMsg(StrEnum):
    # HTTP client errors
    CONNECTION_ERROR = "Connection error in request"
    CONNECTION_TIMEOUT = "Request connection timeout"
    REQUEST_EXCEPTION = "Unexpected error from request"
    # CSRF Token errors
    INVALID_TOKEN = "Invalid CSRF Token"
    TOKEN_COOKIE_ERROR = "Missing CSRF Token Cookie"
    TOKEN_HEADER_ERROR = "Missing CSRF Token Header"
    TOKEN_SIGNATURE_ERROR = "CSRF Token signatures do not match"
    EXPIRED_TOKEN = "CSRF token has expired"
    # Scopus API errors
    QUOTA_EXCEEDED = "API Key has exceeded the request quota"
    RATE_LIMIT_EXCEEDED = "Request rate limit per second exceeded"
    VALIDATE_ERROR = "Error in validate response from Scopus API"
    INVALID_JSON_ERROR = "Invalid JSON response from Scopus API"
    SCOPUS_API_ERROR = "Scopus API error"
    DATA_MISMATCH_ERROR = "Data sum mismatch in response"
    # Application errors
    CANCELLED_ERROR = "Unexpected cancellation of requests"
    INTERNAL_ERROR = "Unexpected internal error occurred"
    SERIALIZE_ERROR = "Error serializing error details"
    ARTICLES_NOT_FOUND = "No articles found"
    CSV_NOT_FOUND = "No CSV file found"
    SLOWAPI_RATE_ERROR = "Request rate limit exceeded"


@unique
class Button(StrEnum):
    PREVIOUS = auto()
    COMBINATION = auto()
    SURVEY = auto()
    DOWNLOAD = auto()


@unique
class DocType(StrEnum):
    AR = auto()  # Article
    AB = auto()  # Abstract Report
    BK = auto()  # Book
    BZ = auto()  # Business Article
    CH = auto()  # Book Chapter
    CP = auto()  # Conference Paper
    CR = auto()  # Conference Review
    ED = auto()  # Editorial
    ER = auto()  # Erratum
    LE = auto()  # Letter
    NO = auto()  # Note
    PR = auto()  # Press Release
    RE = auto()  # Review
    SH = auto()  # Short Survey


@unique
class PubStage(StrEnum):
    AIP = auto()  # Article in Press
    FINAL = auto()  # Final Document


@unique
class SrcType(StrEnum):
    J = auto()  # Journal
    B = auto()  # Book
    K = auto()  # Book Series
    P = auto()  # Conference Proceeding
    R = auto()  # Report
    D = auto()  # Trade Publication


@unique
class SubjArea(StrEnum):
    AGRI = "AGRI"  # Agricultural and Biological Sciences
    ARTS = "ARTS"  # Arts and Humanities
    BIOC = "BIOC"  # Biochemistry, Genetics and Molecular Biology
    BUSI = "BUSI"  # Business, Management and Accounting
    CENG = "CENG"  # Chemical Engineering
    CHEM = "CHEM"  # Chemistry
    COMP = "COMP"  # Computer Science
    DECI = "DECI"  # Decision Sciences
    DENT = "DENT"  # Dentistry
    EART = "EART"  # Earth and Planetary Sciences
    ECON = "ECON"  # Economics, Econometrics and Finance
    ENER = "ENER"  # Energy
    ENGI = "ENGI"  # Engineering
    ENVI = "ENVI"  # Environmental Science
    HEAL = "HEAL"  # Health Professions
    IMMU = "IMMU"  # Immunology and Microbiology
    MATE = "MATE"  # Materials Science
    MATH = "MATH"  # Mathematics
    MEDI = "MEDI"  # Medicine
    NEUR = "NEUR"  # Neuroscience
    NURS = "NURS"  # Nursing
    PHAR = "PHAR"  # Pharmacology, Toxicology and Pharmaceutics
    PHYS = "PHYS"  # Physics and Astronomy
    PSYC = "PSYC"  # Psychology
    SOCI = "SOCI"  # Social Sciences
    VETE = "VETE"  # Veterinary
    MULT = "MULT"  # Multidisciplinary


@unique
class PageRange(StrEnum):
    SHORT = "0-4"  # Short paper
    LONG = "5-"  # Long paper
