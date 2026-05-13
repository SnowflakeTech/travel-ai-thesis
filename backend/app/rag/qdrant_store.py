from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def ensure_collection(reset: bool = False) -> None:
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    exists = client.collection_exists(collection_name)

    if exists and reset:
        client.delete_collection(collection_name=collection_name)
        exists = False

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


def upsert_points(points: list[PointStruct]) -> None:
    if not points:
        return

    client = get_qdrant_client()

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
    )


def build_metadata_filter(
    city: str | None = None,
    category: str | None = None,
) -> Filter | None:
    must_conditions = []

    if city:
        must_conditions.append(
            FieldCondition(
                key="city_normalized",
                match=MatchValue(value=city),
            )
        )

    if category:
        must_conditions.append(
            FieldCondition(
                key="category_normalized",
                match=MatchValue(value=category),
            )
        )

    if not must_conditions:
        return None

    return Filter(must=must_conditions)