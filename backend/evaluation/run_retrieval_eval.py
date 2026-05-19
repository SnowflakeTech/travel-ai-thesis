import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.retriever import retrieve_context


DATASET_PATH = Path("evaluation/datasets/retrieval_eval_questions.json")
RESULT_PATH = Path("evaluation/results/retrieval_results.json")


def normalize_text(text: str | None) -> str:
    if not text:
        return ""

    return (
        text.lower()
        .strip()
        .replace("\\", "/")
        .replace("backend/data/raw/", "")
        .replace("data/raw/", "")
    )


def contains_any(text: str | None, keywords: list[str]) -> bool:
    normalized = normalize_text(text)

    return any(normalize_text(keyword) in normalized for keyword in keywords)


def calculate_city_match(contexts: list[dict], expected_city: str) -> float:
    if not contexts:
        return 0.0

    matched = 0

    for context in contexts:
        if normalize_text(context.get("city")) == normalize_text(expected_city):
            matched += 1

    return matched / len(contexts)


def calculate_category_match(contexts: list[dict], expected_categories: list[str]) -> float:
    if not contexts:
        return 0.0

    matched = 0

    for context in contexts:
        category = context.get("category", "")

        if contains_any(category, expected_categories):
            matched += 1

    return matched / len(contexts)


def calculate_source_file_match(contexts: list[dict], expected_source_files: list[str]) -> float:
    if not contexts:
        return 0.0

    matched = 0

    for context in contexts:
        source_file = normalize_text(context.get("source_file"))

        if any(normalize_text(expected) in source_file for expected in expected_source_files):
            matched += 1

    return matched / len(contexts)


def calculate_hit_at_k(contexts: list[dict], expected_keywords: list[str], k: int) -> int:
    top_k = contexts[:k]

    for context in top_k:
        combined_text = " ".join(
            [
                str(context.get("title", "")),
                str(context.get("category", "")),
                str(context.get("source_file", "")),
                str(context.get("text", "")),
            ]
        )

        if contains_any(combined_text, expected_keywords):
            return 1

    return 0


def main():
    questions = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    results = []

    for item in questions:
        question = item["question"]
        expected_city = item["city"]
        expected_categories = item.get("expected_categories", [])
        expected_source_files = item.get("expected_source_files", [])
        expected_keywords = item.get("expected_keywords", [])

        contexts = retrieve_context(question, limit=7)

        retrieved_summary = [
            {
                "title": context.get("title"),
                "city": context.get("city"),
                "category": context.get("category"),
                "source_file": context.get("source_file"),
                "score": context.get("score"),
                "search_mode": context.get("search_mode"),
            }
            for context in contexts
        ]

        city_match = calculate_city_match(contexts, expected_city)
        category_match = calculate_category_match(contexts, expected_categories)
        source_file_match = calculate_source_file_match(contexts, expected_source_files)
        hit_at_3 = calculate_hit_at_k(contexts, expected_keywords, 3)
        hit_at_5 = calculate_hit_at_k(contexts, expected_keywords, 5)

        result = {
            "id": item["id"],
            "question": question,
            "expected_city": expected_city,
            "expected_categories": expected_categories,
            "expected_source_files": expected_source_files,
            "retrieved": retrieved_summary,
            "city_match": round(city_match, 3),
            "category_match": round(category_match, 3),
            "source_file_match": round(source_file_match, 3),
            "hit_at_3": hit_at_3,
            "hit_at_5": hit_at_5,
        }

        results.append(result)

        print("=" * 80)
        print(item["id"], question)
        print("Retrieved:")
        for retrieved in retrieved_summary:
            print(
                "-",
                retrieved["title"],
                "|",
                retrieved["city"],
                "|",
                retrieved["category"],
                "|",
                retrieved["source_file"],
                "| score:",
                retrieved["score"],
            )
        print("City match:", result["city_match"])
        print("Category match:", result["category_match"])
        print("Source file match:", result["source_file_match"])
        print("Hit@3:", result["hit_at_3"])
        print("Hit@5:", result["hit_at_5"])

    RESULT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    avg_city_match = sum(item["city_match"] for item in results) / len(results)
    avg_category_match = sum(item["category_match"] for item in results) / len(results)
    avg_source_file_match = sum(item["source_file_match"] for item in results) / len(results)
    avg_hit_at_3 = sum(item["hit_at_3"] for item in results) / len(results)
    avg_hit_at_5 = sum(item["hit_at_5"] for item in results) / len(results)

    print("=" * 80)
    print("AVERAGE RETRIEVAL RESULTS")
    print("City Match:", round(avg_city_match, 3))
    print("Category Match:", round(avg_category_match, 3))
    print("Source File Match:", round(avg_source_file_match, 3))
    print("Hit@3:", round(avg_hit_at_3, 3))
    print("Hit@5:", round(avg_hit_at_5, 3))


if __name__ == "__main__":
    main()