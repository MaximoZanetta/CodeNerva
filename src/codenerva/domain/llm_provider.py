from typing import Protocol


class LLMProvider(Protocol):
    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str: ...
