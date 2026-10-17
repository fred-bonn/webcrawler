import sys
from crawl import crawl_page


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("no website provided")
        sys.exit(1)
    if len(args) > 1:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = args[0]

    print(f"starting crawl of: {base_url}")
    pages = {}
    crawl_page(base_url, page_data=pages)

    print(f"crawl finished. pages found: {len(pages)}")

if __name__ == "__main__":
    main()
