import uuid

from qdrant_client.models import PointStruct
from tqdm import tqdm

from app.rag.chunking import create_chunks, place_to_text
from app.rag.data_loader import load_raw_places
from app.rag.embedding import embed_texts
from app.rag.qdrant_store import ensure_collection, upsert_points


BATCH_SIZE = 64


def build_points() -> list[PointStruct]:
    places = load_raw_places()
    all_points: list[PointStruct] = []

    for place in tqdm(places, desc="Building chunks"):
        full_text = place_to_text(place)
        chunks = create_chunks(full_text)
        vectors = embed_texts(chunks)

        for chunk_index, chunk in enumerate(chunks):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[chunk_index],
                payload={
                    "title": place.get("title"),
                    "city": place.get("city"),
                    "city_normalized": place.get("city_normalized"),
                    "category": place.get("category"),
                    "category_normalized": place.get("category_normalized"),
                    "address": place.get("address"),
                    "best_time": place.get("best_time"),
                    "budget": place.get("budget"),
                    "suitable_for": place.get("suitable_for"),
                    "description": place.get("description"),
                    "tips": place.get("tips"),
                    "source_url": place.get("source_url"),
                    "source_file": place.get("source_file"),
                    "latitude": place.get("latitude"),
                    "longitude": place.get("longitude"),
                    "text": chunk,
                    "chunk_index": chunk_index,
                },
            )

            all_points.append(point)

    return all_points


def upsert_in_batches(points: list[PointStruct]) -> None:
    for start in tqdm(range(0, len(points), BATCH_SIZE), desc="Upserting Qdrant"):
        batch = points[start : start + BATCH_SIZE]
        upsert_points(batch)


def main() -> None:
    print("Ensuring Qdrant collection...")
    ensure_collection(reset=True)

    print("Loading, cleaning, chunking and embedding data...")
    points = build_points()

    print(f"Total chunks: {len(points)}")
    upsert_in_batches(points)

    print("RAG ingest completed successfully.")


if __name__ == "__main__":
    main()