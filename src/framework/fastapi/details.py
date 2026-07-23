from src.core.common.types import Headers, SurveyDetails, SurveyParams


def extract_survey_details(
    params: SurveyParams, details: SurveyDetails
) -> tuple[Headers, list[str]]:
    loss = details.total_retrieved - details.total_final
    loss_percent = (
        0.0 if loss == 0 else (loss / details.total_retrieved) * 100.0
    )
    metadata = [
        f"scopus_total={details.search_result.total_results}",
        f"items_per_page={details.search_result.items_per_page}",
        f"pages_count={details.pages_count}",
        f"total_retrieved={details.total_retrieved}",
        f"total_final={details.total_final}",
        f"loss={loss} ({loss_percent:.2f}%)",
    ]
    headers = {
        "X-Combination": params.combination,
        "X-Scopus-Total": str(details.search_result.total_results),
        "X-Total-Retrieved": str(details.total_retrieved),
        "X-Total-Final": str(details.total_final),
        "X-Pages-Count": str(details.pages_count),
        "X-Items-Per-Page": str(details.search_result.items_per_page),
        "X-Search-Limit": str(details.search_headers.limit),
        "X-Search-Remaining": str(details.search_headers.remaining),
        "X-Search-Reset": str(details.search_headers.reset),
        "X-Abstract-Limit": str(details.abstract_headers.limit),
        "X-Abstract-Remaining": str(details.abstract_headers.remaining),
        "X-Abstract-Reset": str(details.abstract_headers.reset),
    }

    return headers, metadata
