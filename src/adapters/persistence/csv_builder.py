from datetime import datetime, timezone

from pandas import DataFrame

from src.core.domain.types import SurveyDetails, SurveyParams
from src.infra.config.config import DIRECTORY, FILE
from src.infra.config.scopus import BOOLEAN_OPERATOR, DATA_SOURCE_NOTE


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
    dataset: DataFrame, params: SurveyParams, details: SurveyDetails
) -> str:
    meta_params = ", ".join(
        f"{field}={value}"
        for field, value in params.model_dump(exclude_none=True).items()
    )
    loss = details.total_retrieved - details.total_final
    loss_percent = (
        0.0 if loss == 0 else (loss / details.total_retrieved) * 100.0
    )
    meta_survey = (
        f"scopus_total={details.search_result.total_results}, "
        f"items_per_page={details.search_result.items_per_page}, "
        f"pages_count={details.pages_count}, "
        f"total_retrieved={details.total_retrieved}, "
        f"total_final={details.total_final}, "
        f"loss={loss} ({loss_percent:.2f}%)"
    )
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # e.g. 2026-05-01

    csv_metadata = (
        f"# GeneratedBy: {_GENERATED_BY}\n"
        f"# Params: {meta_params}\n"
        f"# Survey: {meta_survey}\n"
        f"# Source: {DATA_SOURCE_NOTE.format(date=date)}\n"
    )

    file_path = DIRECTORY / f"{params.api_key}_{FILE}"

    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(csv_metadata)

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
