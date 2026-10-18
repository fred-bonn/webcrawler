import asyncio
import aiohttp
from urllib.parse import urlsplit, urljoin
from typing import TypedDict

import requests
from bs4 import BeautifulSoup, Tag


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(url: str) -> str:
    parsed_url = urlsplit(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if h_tag else ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    p_tag = soup.find("p")
    return p_tag.get_text(strip=True) if p_tag else ""

def get_urls_from_html(html: str, base_url) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for a_tag in soup.find_all("a", href=True):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag["href"]
        if isinstance(href, str) and href:
            try:
                urljoined = urljoin(base_url, href)
                urls.append(urljoined)
            except Exception as e:
                print(f"{str(e)}: {href}")
                
    return urls

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []

    for img_tag in soup.find_all("img", src=True):
        if not isinstance(img_tag, Tag):
            continue
        src = img_tag["src"]
        if isinstance(src, str) and src:
            try:
                urljoined = urljoin(base_url, src)
                image_urls.append(urljoined)
            except Exception as e:
                print(f"{str(e)}: {src}")

    return image_urls

def extract_page_data(html: str, page_url: str) -> PageData:
    return PageData(
        url=page_url,
        heading=get_heading_from_html(html),
        first_paragraph=get_first_paragraph_from_html(html),
        outgoing_links=get_urls_from_html(html, page_url),
        image_urls=get_images_from_html(html, page_url)
    )

class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int = 10, max_pages: int = 100):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: aiohttp.ClientSession | None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task] = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.visited:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            self.visited.add(normalized_url)

        return True

    async def get_html(self, url: str) -> str | None:
        if not self.session:
            return None
        try:
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
                if response.status >= 400:
                    print(f"Error: HTTP {response.status} error while fetching {url}")
                    return None
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"Error: Non-HTML content {content_type} while fetching {url}")
                    return None
                html = await response.text()
                return html
        except Exception as e:
            print(f"Error: Failed to fetch {url}: {e}")
            return None

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return
        if urlsplit(current_url).netloc != self.base_domain:
            return 
        normalized_url = normalize_url(current_url)
        if not await self.add_page_visit(normalized_url):
            return

        print(f"crawling page: {normalized_url}")

        async with self.semaphore:
            html = await self.get_html(current_url)
            if not html:
                return

            page_data = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = page_data

        if self.should_stop:
            return

        tasks: list[asyncio.Task] = []
        for link in page_data["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.append(task)
            task.add_done_callback(self.remove_task_callback)
            self.all_tasks.add(task)
        if tasks:
            await asyncio.gather(*tasks)

    def remove_task_callback(self, task: asyncio.Task) -> None:
        self.all_tasks.discard(task)


    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int) -> dict[str, PageData]:
    async with AsyncCrawler(base_url, max_concurrency=max_concurrency, max_pages=max_pages) as crawler:
        return await crawler.crawl()