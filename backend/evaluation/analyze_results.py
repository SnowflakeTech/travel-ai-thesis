import csv
import json
from pathlib import Path


RETRIEVAL_RESULT_PATH = Path("evaluation/results/retrieval_results.json")
GENERATION_SCORE_PATH = Path("evaluation/results/generation_scores.csv")
REPORT_PATH = Path("evaluation/reports/evaluation_summary.json")


def avg(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def analyze_retrieval() -> dict:
    if not RETRIEVAL_RESULT_PATH.exists():
        return {}

    results = json.loads(RETRIEVAL_RESULT_PATH.read_text(encoding="utf-8"))

    summary = {
        "city_match": round(avg([item["city_match"] for item in results]), 3),
        "category_match": round(avg([item["category_match"] for item in results]), 3),
        "source_file_match": round(avg([item["source_file_match"] for item in results]), 3),
        "hit_at_3": round(avg([item["hit_at_3"] for item in results]), 3),
        "hit_at_5": round(avg([item["hit_at_5"] for item in results]), 3),
        "num_questions": len(results),
    }

    return summary


def analyze_generation() -> dict:
    if not GENERATION_SCORE_PATH.exists():
        return {}

    grouped: dict[str, dict[str, list[float]]] = {}

    with open(GENERATION_SCORE_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            method = row["method"]

            grouped.setdefault(
                method,
                {
                    "relevance": [],
                    "groundedness": [],
                    "hallucination_control": [],
                    "practicality": [],
                    "coherence": [],
                },
            )

            for metric in grouped[method].keys():
                grouped[method][metric].append(float(row[metric]))

    summary = {}

    for method, scores in grouped.items():
        summary[method] = {
            metric: round(avg(values), 2)
            for metric, values in scores.items()
        }

        summary[method]["overall"] = round(
            avg(
                [
                    summary[method]["relevance"],
                    summary[method]["groundedness"],
                    summary[method]["hallucination_control"],
                    summary[method]["practicality"],
                    summary[method]["coherence"],
                ]
            ),
            2,
        )

    return summary


def main():
    retrieval = analyze_retrieval()
    generation = analyze_generation()

    report = {
        "retrieval": retrieval,
        "generation": generation,
    }

    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("=" * 80)
    print("RETRIEVAL SUMMARY")
    print(json.dumps(retrieval, ensure_ascii=False, indent=2))

    print("=" * 80)
    print("GENERATION SUMMARY")
    print(json.dumps(generation, ensure_ascii=False, indent=2))

    print("=" * 80)
    print("Saved report to:", REPORT_PATH)


if __name__ == "__main__":
    main()