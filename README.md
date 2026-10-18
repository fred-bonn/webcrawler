# Web Crawler

Web Crawler is an asynchronous command-line tool that crawls HTML pages on a website and extracts basic page information. It follows links on the starting URL's domain and saves the results as JSON.

## Usage

Run the crawler with a starting URL, the maximum number of concurrent requests, and the maximum number of pages to crawl:

```bash
python main.py <base_url> <max_concurrency> <max_pages>
```

For example:

```bash
python main.py https://example.com 5 100
```

The URL should include its scheme, such as `https://`, and both `max_concurrency` and `max_pages` must be positive whole numbers. The crawler writes the crawled pages to `report.json` in the current directory as a JSON array.
