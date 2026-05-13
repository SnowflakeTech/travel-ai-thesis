import json
from pathlib import Path

from app.rag.cleaning import is_valid_place, normalize_city, normalize_place


RAW_DATA_DIR = Path("data/raw")


def _load_json_file(file_path: Path) -> list[dict]:
    data = json.loads(file_path.read_text(encoding="utf-8-sig"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if isinstance(data.get("places"), list):
            fallback_city = data.get("city", "")
            places = []

            for item in data["places"]:
                if isinstance(item, dict):
                    item = {**item}

                    if not item.get("city") and fallback_city:
                        item["city"] = fallback_city

                    places.append(item)

            return places

    raise ValueError(f"Unsupported JSON structure: {file_path}")


def load_raw_places(raw_data_dir: Path = RAW_DATA_DIR) -> list[dict]:
    json_files = sorted(raw_data_dir.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {raw_data_dir}")

    all_places: list[dict] = []
    skipped_count = 0

    for file_path in json_files:
        raw_places = _load_json_file(file_path)

        fallback_city = normalize_city(file_path.parent.name)

        for raw_place in raw_places:
            place = normalize_place(raw_place, fallback_city=fallback_city)

            if is_valid_place(place):
                place["source_file"] = str(file_path).replace("\\", "/")
                all_places.append(place)
            else:
                skipped_count += 1

    print(f"Loaded JSON files: {len(json_files)}")
    print(f"Valid places: {len(all_places)}")
    print(f"Skipped invalid places: {skipped_count}")

    return all_places