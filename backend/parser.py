from bs4 import BeautifulSoup
import re
from utils.text_cleaner import clean_text

def parse_html(html_content: str) -> dict:
    """
    Parses HTML content to extract the main article title, author, date, and body text.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove unwanted tags like scripts, styles, forms, headers, footers
    for element in soup(["script", "style", "nav", "footer", "header", "form", "aside", "noscript", "meta"]):
        if element.name == "meta" and element.get("name", "").lower() in ["author", "article:author", "article:published_time"]:
            continue # Keep specific metadata
        element.decompose()
        
    # Attempt to find title
    title = soup.title.string.strip() if soup.title and soup.title.string else "Unknown Title"
    if title == "Unknown Title" or "Error" in title:
        h1 = soup.find('h1')
        if h1:
            title = h1.text.strip()
            
    # Attempt to find author (basic heuristics)
    author = "Unknown Author"
    author_meta = soup.find("meta", attrs={"name": re.compile(r"author", re.IGNORECASE)})
    if author_meta and author_meta.get("content"):
        author = author_meta["content"].strip()
    else:
        author_element = soup.find(class_=re.compile(r"author|byline", re.IGNORECASE))
        if author_element:
            author = author_element.text.strip()
            
    # Attempt to find date
    date = "Unknown Date"
    date_meta = soup.find("meta", attrs={"property": "article:published_time"})
    if date_meta and date_meta.get("content"):
        date = date_meta["content"].strip()
    else:
        date_element = soup.find(class_=re.compile(r"date|time|published", re.IGNORECASE))
        if date_element:
            date = date_element.text.strip()
            
    # Attempt to extract main text from paragraphs
    # Prioritize <article> or main content div, then fallback to all <p>
    article_container = soup.find('article') or soup.find("main") or soup.find(id=re.compile(r"content|main", re.IGNORECASE))
    
    if article_container:
        paragraphs = article_container.find_all('p')
    else:
        paragraphs = soup.find_all('p')
        
    # Extract text from paragraphs and clean it.
    texts = []
    for p in paragraphs:
        txt = clean_text(p.text)
        # Exclude very short paragraphs which are often captions or navigation links.
        if len(txt) > 30:
            texts.append(txt)
    
    full_text = " ".join(texts)
    
    return {
        "title": clean_text(title),
        "author": clean_text(author) if author else "Unknown Author",
        "date": clean_text(date) if date else "Unknown Date",
        "text": full_text
    }
