import sys


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

if __name__ == "__main__":
    main()
