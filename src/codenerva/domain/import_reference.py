from dataclasses import dataclass
from uuid import UUID, uuid5

IMPORT_REFERENCE_NAMESPACE = UUID("18b69007-9398-4cbb-b745-4da91ba94425")


@dataclass(frozen=True, slots=True)
class ImportReference:
    id: UUID
    source_file_id: UUID
    module: str
    imported_name: str | None
    alias: str | None
    line: int

    @classmethod
    def create(
        cls,
        *,
        source_file_id: UUID,
        module: str,
        imported_name: str | None,
        alias: str | None,
        line: int,
    ) -> "ImportReference":
        normalized_module = module.strip()

        if not normalized_module:
            raise ValueError("Import module cannot be empty.")

        if line <= 0:
            raise ValueError("Import line must be positive.")

        normalized_imported_name = imported_name.strip() if imported_name else None

        normalized_alias = alias.strip() if alias else None

        import_id = uuid5(
            IMPORT_REFERENCE_NAMESPACE,
            (
                f"{source_file_id}:"
                f"{normalized_module}:"
                f"{normalized_imported_name}:"
                f"{normalized_alias}:"
                f"{line}"
            ),
        )

        return cls(
            id=import_id,
            source_file_id=source_file_id,
            module=normalized_module,
            imported_name=normalized_imported_name,
            alias=normalized_alias,
            line=line,
        )
