import sys
import asyncio
from crawl import crawl_site_async
from json_report import write_json_report


async def main():
    args = sys.argv
    if len(args) < 4:
        print("not enough arguments provided")
        print("usage: main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)
    if len(args) > 4:
        print("too many arguments provided")
        print("usage: main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)
    if not args[2].isdigit():
        print("max_concurrency must be an integer")
        sys.exit(1)
    if not args[3].isdigit():
        print("max_pages must be an integer")
        sys.exit(1)
    
    base_url = args[1]
    max_concurrency = int(args[2])
    max_pages = int(args[3])

    if max_concurrency <= 0:
        print("max_concurrency must be a positive integer")
        sys.exit(1)
    if max_pages <= 0:
        print("max_pages must be a positive integer")
        sys.exit(1)

    print(f"starting crawl of: {base_url}")
    print(f"max_concurrency: {max_concurrency}, max_pages: {max_pages}")

    page_data = await crawl_site_async(base_url, max_concurrency=max_concurrency, max_pages=max_pages)

    print(f"crawl finished.")
    print(f"total pages crawled: {len(page_data)}")
    write_json_report(page_data)
    print("JSON report written to report.json")

if __name__ == "__main__":
    asyncio.run(main())
