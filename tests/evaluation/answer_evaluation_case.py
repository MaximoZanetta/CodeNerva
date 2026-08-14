from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnswerEvaluationCase:
    name: str
    question: str

    expected_facts: tuple[str, ...]
    expected_sources: tuple[str, ...]

    minimum_fact_coverage: float = 0.80
    minimum_source_coverage: float = 0.80
