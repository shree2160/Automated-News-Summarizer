from bs4 import BeautifulSoup
import re
from utils.text_cleaner import clean_text

def parse_html(html_content: str) -> dict:
    """
    Parses HTML content to extract the main article title, author, date, and body text.
    """
    # Use lxml for better speed and handling of malformed HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove unwanted tags that don't contain article content
    unwanted = ["script", "style", "nav", "footer", "header", "form", "aside", "noscript", "meta", "iframe", "button", "input"]
    for element in soup(unwanted):
        if element.name == "meta" and element.get("name", "").lower() in ["author", "article:author", "article:published_time"]:
            continue 
        element.decompose()
        
    # Attempt to find title (Title tag or H1)
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.split('|')[0].split('-')[0].strip()
    
    if not title or len(title) < 5:
        h1 = soup.find('h1')
        if h1: title = h1.text.strip()
            
    # Author detection
    author = "Unknown Author"
    # Common author patterns
    author_meta = soup.find("meta", attrs={"name": re.compile(r"author", re.IGNORECASE)}) or \
                  soup.find("meta", attrs={"property": "article:author"})
    if author_meta and author_meta.get("content"):
        author = author_meta["content"].strip()
    else:
        author_element = soup.find(class_=re.compile(r"author|byline|writer", re.IGNORECASE))
        if author_element:
            author = author_element.text.strip()
            
    # Date detection
    date = "Unknown Date"
    date_meta = soup.find("meta", attrs={"property": "article:published_time"}) or \
                soup.find("meta", attrs={"name": re.compile(r"date|pub", re.IGNORECASE)})
    if date_meta and date_meta.get("content"):
        date = date_meta["content"].strip().split('T')[0] # Usually ISO format
    else:
        date_element = soup.find(class_=re.compile(r"date|time|published", re.IGNORECASE))
        if date_element:
            date = date_element.text.strip()
            
    # Article extraction - prioritize specialized containers
    article_container = soup.find('article') or \
                        soup.find("main") or \
                        soup.find(id=re.compile(r"article|story|content|main-content", re.IGNORECASE)) or \
                        soup.find(class_=re.compile(r"article-body|story-content|post-content", re.IGNORECASE))
    
    if article_container:
        paragraphs = article_container.find_all('p')
    else:
        # Fallback to finding the container with the most paragraph text
        bodies = soup.find_all(['div', 'section', 'article'])
        max_p_len = 0
        article_container = None
        for b in bodies:
            ps = b.find_all('p', recursive=False)
            current_len = sum(len(p.text) for p in ps)
            if current_len > max_p_len:
                max_p_len = current_len
                article_container = b
        
        paragraphs = article_container.find_all('p') if article_container else soup.find_all('p')
        
    # Filter and clean paragraph text
    texts = []
    for p in paragraphs:
        txt = clean_text(p.text)
        # Exclude very short strings, common CTA patterns
        if len(txt) > 40 and not any(cta in txt.lower() for cta in ["copyright", "rights reserved", "read more", "sign up", "follow us"]):
            texts.append(txt)
    
    full_text = " ".join(texts)
    
    return {
        "title": clean_text(title) if title else "Unknown Title",
        "author": clean_text(author) if author else "Unknown Author",
        "date": clean_text(date) if date else "Unknown Date",
        "text": full_text
    }
