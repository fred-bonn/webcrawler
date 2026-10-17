from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag

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