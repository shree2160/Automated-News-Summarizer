import requests
from bs4 import BeautifulSoup
import re

class ScraperService:
    @staticmethod
    def fetch_html(url: str) -> str:
        """
        Fetches the raw HTML content from a given URL.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch content from {url}: {str(e)}")

class ParserService:
    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extracts clean article text from HTML content.
        Uses common article body selectors and cleans UI elements.
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Remove obvious non-content zones FIRST
        for element in soup(["script", "style", "header", "footer", "nav", "aside", "form", "iframe", "noscript"]):
            element.decompose()
            
        # 2. Heuristic: Remove elements with typical noise classes/IDs
        noise_selectors = [
            ".sidebar", ".header", ".footer", ".nav", ".menu", ".ad-container", 
            ".social-share", "#comments", ".related-posts", "#sidebar", ".article-footer"
        ]
        for selector in noise_selectors:
            for tag in soup.select(selector):
                tag.decompose()

        # 3. Try to find the BEST container for the article text
        # Common news article containers
        main_selectors = [
            "article", 
            "[itemprop='articleBody']", 
            ".article-content", 
            ".entry-content", 
            ".article-body", 
            "#article-body"
        ]
        
        main_tag = None
        for selector in main_selectors:
            main_tag = soup.select_one(selector)
            if main_tag:
                break
                
        source = main_tag if main_tag else soup
        
        # 4. Extract text from paragraphs within the chosen container
        paragraphs = source.find_all("p")
        text_content = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # 5. Final cleaning
        text_content = re.sub(r' +', ' ', text_content).strip()
        
        if not text_content:
            # Fallback to simple text extraction if no paragraphs found in container
            text_content = source.get_text(separator=' ', strip=True)
            text_content = re.sub(r'\s+', ' ', text_content).strip()

        if len(text_content) < 100:
             raise Exception("Extracted content is too short to summarize. The site might be protected or have zero text.")

        return text_content

    @staticmethod
    def extract_metadata(html: str) -> dict:
        """
        Extracts metadata like title, author, and date.
        """
        soup = BeautifulSoup(html, "html.parser")
        metadata = {
            "title": soup.title.string if soup.title else "Unknown Title",
            "author": "Unknown",
            "date": "Unknown"
        }
        
        # Try to find author in common meta tags
        author_tag = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
        if author_tag:
            metadata["author"] = author_tag.get("content")
            
        # Try to find date
        date_tag = soup.find("meta", attrs={"property": "article:published_time"}) or soup.find("meta", attrs={"name": "date"})
        if date_tag:
            metadata["date"] = date_tag.get("content")
            
        return metadata
