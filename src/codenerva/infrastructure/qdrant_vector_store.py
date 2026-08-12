from uuid import UUID

from qdrant_client import QdrantClient, models

from codenerva.domain.vector_record import VectorRecord
from codenerva.domain.vector_search_result import VectorSearchResult
from codenerva.domain.vector_store import VectorStore


class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        *,
        client: QdrantClient,
        collection_name: str,
        dimensions: int,
    ) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive.")

        self._client = client
        self._collection_name = collection_name
        self._dimensions = dimensions

        self._ensure_collection()

    def save_many(
        self,
        records: tuple[VectorRecord, ...],
    ) -> None:
        if not records:
            return

        points = [
            models.PointStruct(
                id=str(record.chunk_id),
                vector=list(record.vector),
                payload={
                    "snapshot_id": str(record.snapshot_id),
                    "source_file_id": str(record.source_file_id),
                    "symbol_id": str(record.symbol_id),
                    "relative_path": record.relative_path,
                    "language": record.language,
                    "qualified_name": (record.qualified_name),
                    "symbol_kind": record.symbol_kind,
                },
            )
            for record in records
        ]

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
            wait=True,
        )

    def get_by_chunk_id(
        self,
        chunk_id: UUID,
    ) -> VectorRecord | None:
        records = self._client.retrieve(
            collection_name=self._collection_name,
            ids=[str(chunk_id)],
            with_payload=True,
            with_vectors=True,
        )

        if not records:
            return None

        point = records[0]

        if point.payload is None:
            return None

        if point.vector is None:
            return None

        payload = point.payload

        return VectorRecord(
            chunk_id=chunk_id,
            vector=tuple(float(value) for value in point.vector),
            snapshot_id=UUID(str(payload["snapshot_id"])),
            source_file_id=UUID(str(payload["source_file_id"])),
            symbol_id=UUID(str(payload["symbol_id"])),
            relative_path=str(payload["relative_path"]),
            language=str(payload["language"]),
            qualified_name=str(payload["qualified_name"]),
            symbol_kind=str(payload["symbol_kind"]),
        )

    def search(
        self,
        *,
        query_vector: tuple[float, ...],
        top_k: int,
        snapshot_id: UUID,
    ) -> tuple[VectorSearchResult, ...]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if not query_vector:
            raise ValueError("query_vector cannot be empty.")

        if len(query_vector) != self._dimensions:
            raise ValueError("query_vector has invalid dimensions.")

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=list(query_vector),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="snapshot_id",
                        match=models.MatchValue(
                            value=str(snapshot_id),
                        ),
                    )
                ]
            ),
            limit=top_k,
            with_payload=True,
            with_vectors=True,
        )

        results: list[VectorSearchResult] = []

        for point in response.points:
            if point.payload is None:
                continue

            if point.vector is None:
                continue

            payload = point.payload

            record = VectorRecord(
                chunk_id=UUID(str(point.id)),
                vector=tuple(float(value) for value in point.vector),
                snapshot_id=UUID(str(payload["snapshot_id"])),
                source_file_id=UUID(str(payload["source_file_id"])),
                symbol_id=UUID(str(payload["symbol_id"])),
                relative_path=str(payload["relative_path"]),
                language=str(payload["language"]),
                qualified_name=str(payload["qualified_name"]),
                symbol_kind=str(payload["symbol_kind"]),
            )

            results.append(
                VectorSearchResult(
                    record=record,
                    score=float(point.score),
                )
            )

        return tuple(results)

    def _ensure_collection(
        self,
    ) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=models.VectorParams(
                size=self._dimensions,
                distance=models.Distance.COSINE,
            ),
        )
