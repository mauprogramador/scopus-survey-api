from datetime import datetime

from pandas import DataFrame

from src.core.common.types import SurveyParams
from src.core.config.config import DIRECTORY, FILE
from src.core.config.scopus import BOOLEAN_OPERATOR, DATA_SOURCE_NOTE


_GENERATED_BY = (
    "ScopusSurveyAPI https://github.com/mauprogramador/scopus-survey-api"
)
_COLUMN_TRANSLATION = {
    "url": "Article Preview Page URL",
    "scopus_id": "Scopus ID",
    "authors": "Authors",
    "title": "Title",
    "publication_name": "Publication Name",
    "abstract": "Abstract",
    "date": "Date",
    "eid": "Electronic ID",
    "doi": "DOI",
    "volume": "Volume",
    "citations": "Citations",
}


def write_csv_file(
    dataset: DataFrame, params: SurveyParams, metadata: list[str]
) -> str:
    csv_metadata = {"GeneratedBy": _GENERATED_BY}

    params_obj = params.model_dump(exclude_none=True)
    params_obj.update(
        {
            "keywords": params.keywords,
            "combination": params.combination,
            "ratio": params.ratio,
        }
    )

    csv_metadata["Params"] = ", ".join(
        [f"{field}={value}" for field, value in params_obj.items()]
    )
    csv_metadata["Survey"] = ", ".join(metadata)

    date = datetime.now().strftime("%B %d, %Y")  # e.g. May 01, 2026
    csv_metadata["Source"] = DATA_SOURCE_NOTE.format(date=date)

    file_path = DIRECTORY / f"{params.api_key}_{FILE}"

    with file_path.open(mode="w", encoding="utf-8") as file:
        for field, value in csv_metadata.items():
            file.write(f"# {field}: {value}\n")

        dataset.rename(columns=_COLUMN_TRANSLATION).to_csv(
            file,
            sep=";",
            na_rep="",
            header=True,
            index=False,
            encoding="utf-8",
        )

    survey_keywords = (
        params.combination.replace(BOOLEAN_OPERATOR, "-")
        .replace(" ", "-")
        .lower()
    )
    filename = f"{params.api_key}_{survey_keywords}_{FILE}"

    return filename
