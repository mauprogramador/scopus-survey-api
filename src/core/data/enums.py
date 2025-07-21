from enum import StrEnum, auto, unique


@unique
class Lang(StrEnum):
    EN_US = "en-US"
    PT_BR = "pt-BR"


@unique
class ScopusCode(StrEnum):
    QUOTA = "QUOTA_EXCEEDED"
    RATE_LIMIT = "RATE_LIMIT_EXCEEDED"


class Column:
    URL = "Article Preview Page URL"
    AUTHORS = "Authors"
    TITLE = "Title"
    DATE = "Date"

    DROP = [TITLE, AUTHORS]
    FILTER = [AUTHORS, TITLE, DATE]


@unique
class Templates(StrEnum):
    INDEX = "index.html"
    ERROR = "error.html"


@unique
class Button(StrEnum):
    PREVIOUS = auto()
    COMBINATION = auto()
    SEARCH = auto()
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
