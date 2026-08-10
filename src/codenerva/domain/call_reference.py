from dataclasses import dataclass
from uuid import UUID, uuid5

CALL_REFERENCE_NAMESPACE = UUID("d9e22871-8627-4b61-a4d2-6bcbf1430a1d")


@dataclass(frozen=True, slots=True)
class CallReference:
    id: UUID
    source_file_id: UUID
    caller_symbol_id: UUID
    callee_name: str
    line: int

    @classmethod
    def create(
        cls,
        *,
        source_file_id: UUID,
        caller_symbol_id: UUID,
        callee_name: str,
        line: int,
    ) -> "CallReference":
        normalized_name = callee_name.strip()

        if not normalized_name:
            raise ValueError("Call target name cannot be empty.")

        if line <= 0:
            raise ValueError("Call line must be positive.")

        reference_id = uuid5(
            CALL_REFERENCE_NAMESPACE,
            (f"{source_file_id}:{caller_symbol_id}:{normalized_name}:{line}"),
        )

        return cls(
            id=reference_id,
            source_file_id=source_file_id,
            caller_symbol_id=caller_symbol_id,
            callee_name=normalized_name,
            line=line,
        )
