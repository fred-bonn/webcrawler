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

def get_html(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if response.status_code >= 400:
        raise Exception(f"HTTP error: {response.status_code} {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"non-HTML response: {content_type}")

    return response.text

def crawl_page(base_url: str, current_url: str | None = None, page_data: dict[str, PageData] | None = None) -> None:
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    if urlsplit(base_url).netloc != urlsplit(current_url).netloc:
        return
    
    normalized_url = normalize_url(current_url)
    if normalized_url in page_data:
        return

    print(f"crawling: {current_url}")
    
    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"failed to crawl {current_url}: {e}")
        return

    page_info = extract_page_data(html, current_url)
    page_data[normalized_url] = page_info

    for next_url in page_info["outgoing_links"]:
        crawl_page(base_url, next_url, page_data)