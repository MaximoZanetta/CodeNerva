from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnswerMetrics:
    fact_coverage: float
    source_coverage: float

    expected_fact_count: int
    matched_fact_count: int

    expected_source_count: int
    matched_source_count: int


def evaluate_answer(
    *,
    answer: str,
    expected_facts: tuple[str, ...],
    expected_sources: tuple[str, ...],
) -> AnswerMetrics:
    if not expected_facts:
        raise ValueError("expected_facts cannot be empty.")

    normalized_answer = answer.lower()

    matched_facts = sum(
        1 for fact in expected_facts if fact.lower() in normalized_answer
    )

    matched_sources = sum(
        1 for source in expected_sources if source.lower() in normalized_answer
    )

    fact_coverage = matched_facts / len(expected_facts)

    source_coverage = (
        matched_sources / len(expected_sources) if expected_sources else 1.0
    )

    return AnswerMetrics(
        fact_coverage=fact_coverage,
        source_coverage=source_coverage,
        expected_fact_count=len(expected_facts),
        matched_fact_count=matched_facts,
        expected_source_count=len(expected_sources),
        matched_source_count=matched_sources,
    )
