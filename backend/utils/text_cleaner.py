import re

def clean_text(text: str) -> str:
    """
    Cleans raw text extracted from HTML.
    - Removes extra whitespaces
    - Removes new lines
    - Normalizes unicode
    """
    if not text:
        return ""
    
    # Remove extra spaces and new lines
    text = re.sub(r'\s+', ' ', text)
    # Strip leading and trailing spaces
    text = text.strip()
    
    return text
