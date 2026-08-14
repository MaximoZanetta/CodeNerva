from openai import OpenAI

from codenerva.domain.llm_provider import LLMProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(
        self,
        *,
        model: str = "gpt-5-mini",
        client: OpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or OpenAI()

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        response = self._client.responses.create(
            model=self._model,
            store=False,
            instructions=(
                "You are CodeNerva, an assistant that answers questions "
                "about software repositories using only the repository "
                "context provided to you. "
                "Ground every technical claim in the provided context. "
                "Do not invent files, symbols, imports, calls, behavior, "
                "runtime effects, architecture, or implementation details. "
                "When describing relationships between code elements, "
                "only state a relationship as factual if the provided "
                "context directly supports it through code or graph "
                "relations. "
                "Only make an inference when it is necessary to answer the "
                "user's question and it follows directly from multiple pieces "
                "of repository context. "
                "Do not add general programming, framework, or library behavior "
                "that is not demonstrated by the provided repository context. "
                "If an inference is necessary, clearly label it as an inference "
                "rather than a confirmed fact. "
                "Prefer concrete explanations using exact symbol names "
                "and file paths when they are available. "
                "For execution-flow questions, explain the flow in order "
                "from caller to callee when the context supports that order. "
                "For architecture or structure questions, organize the "
                "answer by the relevant files, classes, functions, or layers "
                "present in the context. "
                "If the context does not contain enough evidence to answer "
                "part of the question, explicitly say which part cannot be "
                "determined from the provided context. "
                "Do not speculate beyond the repository context. "
                "Do not suggest that additional repository files were seen "
                "unless they are actually present in the context. "
                "Be concise but complete. "
                "Do not repeat the same information unnecessarily."
            ),
            input=(
                "Use the following repository context as your only source "
                "of evidence.\n\n"
                "=== REPOSITORY CONTEXT ===\n"
                f"{context}\n"
                "=== END REPOSITORY CONTEXT ===\n\n"
                "=== QUESTION ===\n"
                f"{question}\n"
                "=== END QUESTION ==="
            ),
        )

        return response.output_text
