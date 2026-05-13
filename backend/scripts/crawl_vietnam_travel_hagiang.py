import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


URL = "https://vietnam.travel/places-to-go/northern-vietnam/ha-giang"

OUTPUT_DIR = Path("data/raw/hagiang")
OUTPUT_FILE = OUTPUT_DIR / "attractions.json"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def clean_text(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def get_page_text_blocks(soup: BeautifulSoup) -> list[str]:
    blocks = []

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "p"]):
        text = clean_text(tag.get_text(" ", strip=True))

        if not text:
            continue

        if text.lower() in {
            "overview",
            "gallery",
            "you may also like",
            "nearby places",
            "sign up for our newsletter",
            "follow us on",
        }:
            continue

        if "Receive new travel stories" in text:
            continue

        blocks.append(text)

    return blocks


def find_text_after_heading(blocks: list[str], heading: str) -> str:
    for index, block in enumerate(blocks):
        if block.lower() == heading.lower():
            if index + 1 < len(blocks):
                return blocks[index + 1]

    return ""


def extract_related_links(soup: BeautifulSoup) -> list[str]:
    links = []

    for a_tag in soup.find_all("a", href=True):
        title = clean_text(a_tag.get_text(" ", strip=True))
        href = a_tag["href"]

        if not title:
            continue

        if "ha giang" not in title.lower() and "outdoor activities" not in title.lower():
            continue

        full_url = urljoin(URL, href)

        if full_url not in [item["url"] for item in links]:
            links.append(
                {
                    "title": title,
                    "url": full_url,
                }
            )

    return links


def build_places(blocks: list[str], related_links: list[dict[str, str]]) -> list[dict]:
    overview = ""

    for block in blocks:
        if block.startswith("A border province"):
            overview = block
            break

    ma_pi_leng = find_text_after_heading(blocks, "Drive Ma Pi Leng Pass")
    hills = find_text_after_heading(blocks, "Get lost in the hills")
    palace = find_text_after_heading(blocks, "Visit the Sa Phin H'Mong Palace")
    flagpole = find_text_after_heading(blocks, "See the king of flagpoles")
    weather = find_text_after_heading(blocks, "Ha Giang Weather")
    transport = find_text_after_heading(blocks, "Ha Giang Transport")

    common_tips = "Thích hợp đi theo dạng road trip, cần kiểm tra thời tiết và chuẩn bị kỹ nếu di chuyển bằng xe máy."

    places = [
        {
            "title": "Ha Giang",
            "city": "Hà Giang",
            "category": "destination",
            "address": "Hà Giang, Việt Nam",
            "best_time": weather,
            "budget": "",
            "suitable_for": ["road trip", "thiên nhiên", "khám phá", "người thích cảnh núi"],
            "description": overview,
            "tips": common_tips,
            "source_url": URL,
            "latitude": None,
            "longitude": None,
        },
        {
            "title": "Ma Pi Leng Pass",
            "city": "Hà Giang",
            "category": "nature",
            "address": "Hà Giang, Việt Nam",
            "best_time": "Nên đi ban ngày, thời tiết khô ráo để ngắm cảnh và di chuyển an toàn.",
            "budget": "",
            "suitable_for": ["road trip", "ngắm cảnh", "chụp ảnh", "người thích cung đường đèo"],
            "description": ma_pi_leng,
            "tips": "Nên đi chậm, giữ an toàn khi di chuyển bằng xe máy hoặc ô tô qua đèo.",
            "source_url": URL,
            "latitude": None,
            "longitude": None,
        },
        {
            "title": "Quan Ba Pass and Dong Van Karst Plateau Geopark",
            "city": "Hà Giang",
            "category": "nature",
            "address": "Hà Giang, Việt Nam",
            "best_time": weather,
            "budget": "",
            "suitable_for": ["trekking", "thiên nhiên", "địa chất", "người thích núi đá"],
            "description": hills,
            "tips": "Phù hợp với người thích trekking và khám phá cảnh quan núi đá.",
            "source_url": URL,
            "latitude": None,
            "longitude": None,
        },
        {
            "title": "Sa Phin H'Mong Palace",
            "city": "Hà Giang",
            "category": "culture",
            "address": "Sà Phìn, Hà Giang, Việt Nam",
            "best_time": "Có thể tham quan trong ngày, nên kết hợp với lịch trình Đồng Văn.",
            "budget": "",
            "suitable_for": ["văn hóa", "lịch sử", "kiến trúc", "tham quan"],
            "description": palace,
            "tips": "Nên dành thời gian tìm hiểu bối cảnh lịch sử và kiến trúc của dinh thự.",
            "source_url": URL,
            "latitude": None,
            "longitude": None,
        },
        {
            "title": "Lung Cu Flag Tower",
            "city": "Hà Giang",
            "category": "culture",
            "address": "Lũng Cú, Hà Giang, Việt Nam",
            "best_time": "Chiều muộn là thời điểm dễ chịu hơn để leo bậc thang.",
            "budget": "",
            "suitable_for": ["tham quan", "văn hóa", "chụp ảnh", "ngắm cảnh"],
            "description": flagpole,
            "tips": "Trang gốc gợi ý nên đến vào cuối buổi chiều vì thời tiết bớt nóng, việc leo khoảng 200 bậc sẽ nhẹ hơn.",
            "source_url": URL,
            "latitude": None,
            "longitude": None,
        },
    ]

    for place in places:
        if not place["description"]:
            place["description"] = "Thông tin mô tả sẽ được bổ sung sau khi làm sạch dữ liệu."

        if not place["best_time"]:
            place["best_time"] = weather

        place["related_links"] = related_links

    return places


def main() -> None:
    print(f"Đang crawl: {URL}")

    html = fetch_html(URL)
    soup = BeautifulSoup(html, "lxml")

    blocks = get_page_text_blocks(soup)
    related_links = extract_related_links(soup)
    places = build_places(blocks, related_links)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(places, file, ensure_ascii=False, indent=2)

    print(f"Đã lưu {len(places)} địa điểm vào: {OUTPUT_FILE}")

    time.sleep(1)


if __name__ == "__main__":
    main()