import json

from crawl import PageData

def write_json_report(page_data: dict[str, PageData], filename: str = "report.json") -> None:
    sorted_pages = sorted(page_data.values(), key=lambda p: p["url"])
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted_pages, f, ensure_ascii=False, indent=2)