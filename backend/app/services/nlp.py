from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

# Ensure nltk resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

class NLPService:
    def __init__(self):
        # Initialize pipelines (this will download models on first run)
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def generate_summary(self, text: str, length_preference: str = "medium", title: str = "") -> dict:
        """
        Generates a summary of the article text.
        title (optional) to give context.
        """
        # Adjust max/min lengths based on preference
        if length_preference == "short":
            max_len, min_len = 80, 20
        elif length_preference == "long":
            max_len, min_len = 250, 100
        else: # medium
            max_len, min_len = 150, 40

        # HuggingFace transformers have a token limit (usually 1024)
        # We'll prepend the title as context
        input_text = f"{title}. {text}" if title else text
        truncated_text = input_text[:4000] 

        summary_output = self.summarizer(truncated_text, max_length=max_len, min_length=min_len, do_sample=False)
        summary_text = summary_output[0]['summary_text']

        # Format into bullets
        sentences = sent_tokenize(summary_text)
        
        return {
            "paragraph": summary_text,
            "bullets": [s.strip() for s in sentences if s.strip()]
        }

    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyzes the sentiment of the article.
        """
        # Analyze the first part of the text for sentiment
        truncated_text = text[:512] # DistilBERT token limit is 512
        result = self.sentiment_analyzer(truncated_text)[0]
        
        return {
            "label": result['label'],
            "score": round(result['score'], 4)
        }
