from bs4 import BeautifulSoup
import re
from utils.text_cleaner import clean_text

def parse_html(html_content: str) -> dict:
    """
    Parses HTML content to extract the main article title, author, date, and body text.
    Correctly handles non-standard paragraph structures (like Times of India).
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Pre-select and remove noisy containers
    noise_selectors = [
        "script", "style", "nav", "footer", "header", "form", "aside", "noscript", 
        "iframe", "button", "input", ".ad-container", "#comments", ".social-share",
        ".author-desc", ".author_desc", "#auhtor_widget", "#author_widget", ".authorComment",
        ".Wh0Gu", ".cdatainfo", ".Wcsek", ".related-stories", ".trending-topics", ".MwN2O"
    ]
    for sel in noise_selectors:
        for element in soup.select(sel):
            element.decompose()
            
    # Title detection
    title_element = soup.select_one("h1.HNMDR") or soup.find("h1")
    if title_element:
        title = title_element.text.strip()
    else:
        title = soup.title.string.split('|')[0].split('-')[0].strip() if soup.title else "Unknown Title"
            
    # Author detection
    author = "Unknown Author"
    author_selectors = ["meta[name='author']", "meta[property='article:author']", ".author-name", ".byline", ".writer-name"]
    for sel in author_selectors:
        el = soup.select_one(sel)
        if el:
            author = el.get("content", el.text).strip()
            break
            
    # Article extraction - prioritize specialized containers
    article_container = soup.select_one("div._s30J") or \
                        soup.find('article') or \
                        soup.find("main") or \
                        soup.find(id=re.compile(r"article|story|content|main-content", re.IGNORECASE)) or \
                        soup.find(class_=re.compile(r"article-body|story-content|post-content", re.IGNORECASE))
    
    texts = []
    if article_container:
        # Clean internal noise before extraction
        for noise in article_container.select(".Wh0Gu, .cdatainfo, .author_desc, .authorComment"):
            noise.decompose()
            
        # Strategy A: Check for <p> tags
        paragraphs = article_container.find_all('p')
        if paragraphs and len(paragraphs) > 1:
            for p in paragraphs:
                txt = clean_text(p.text)
                if len(txt) > 40: texts.append(txt)
        else:
            # Strategy B: Extract text blocks separated by <br>, <div> or specialized break spans
            # We'll use get_text with a newline separator and then split/filter
            raw_text = article_container.get_text(separator="\n")
            blocks = raw_text.split("\n")
            for block in blocks:
                txt = clean_text(block)
                # Filter out short fragments or navigation-like text
                if len(txt) > 50 and not any(cta in txt.lower() for cta in ["copyright", "rights reserved", "read more", "sign up", "follow us"]):
                    texts.append(txt)
    
    # Final Fallback: If still nothing, try all <p> in the whole document as a last resort
    if not texts:
        for p in soup.find_all('p'):
            txt = clean_text(p.text)
            if len(txt) > 60: texts.append(txt)
    
    full_text = " ".join(texts)
    
    # Date detection (Simple fallback)
    date = "Unknown Date"
    date_meta = soup.find("meta", attrs={"property": "article:published_time"}) or \
                soup.find("meta", attrs={"name": re.compile(r"date|pub", re.IGNORECASE)})
    if date_meta and date_meta.get("content"):
        date = date_meta["content"].strip().split('T')[0]
    
    return {
        "title": clean_text(title) if title else "Unknown Title",
        "author": clean_text(author) if author else "Unknown Author",
        "date": clean_text(date) if date else "Unknown Date",
        "text": full_text
    }
