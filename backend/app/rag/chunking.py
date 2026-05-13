from langchain_text_splitters import RecursiveCharacterTextSplitter


def place_to_text(place: dict) -> str:
    suitable_for = ", ".join(place.get("suitable_for", []))

    parts = [
        f"Tên địa điểm: {place.get('title')}",
        f"Thành phố: {place.get('city')}",
        f"Loại hình: {place.get('category')}",
        f"Địa chỉ: {place.get('address')}",
        f"Thời điểm phù hợp: {place.get('best_time')}",
        f"Ngân sách tham khảo: {place.get('budget')}",
        f"Phù hợp với: {suitable_for}",
        f"Mô tả: {place.get('description')}",
        f"Lưu ý: {place.get('tips')}",
        f"Nguồn: {place.get('source_url')}",
    ]

    return "\n".join(part for part in parts if part and not part.endswith(": "))


def create_chunks(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_text(text)