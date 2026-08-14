from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationCase:
    name: str
    question: str
    expected_symbols: tuple[str, ...]
    top_k: int = 4
    max_items: int = 8
    max_chars: int = 16000

    minimum_recall: float = 0.80
    minimum_precision: float = 0.50
    minimum_mrr: float = 0.50
    minimum_ndcg: float = 0.70
