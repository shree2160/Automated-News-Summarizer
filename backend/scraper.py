import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_article(url: str) -> str:
    """
    Fetches raw HTML from a given URL with browser-like headers, URL validation, and retry logic.
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL provided: {url}")
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch article: {e}")
        raise ValueError(f"Failed to retrieve article from {url}. Error: {e}")
