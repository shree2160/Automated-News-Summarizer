from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import logging

logger = logging.getLogger(__name__)

class SummarizerEngine:
    def __init__(self):
        self._model = None
        self._model_name = "facebook/bart-large-cnn"
        
    def load_model(self):
        if self._model is None:
            logger.info("Loading summarization model...")
            self._model = pipeline("summarization", model=self._model_name)
            
            try:
                sent_tokenize("Test sentence.")
            except LookupError:
                logger.info("Downloading NLTK punkt_tab...")
                nltk.download('punkt')
                nltk.download('punkt_tab')
                
            logger.info("Summarization model loaded.")
            
    def summarize(self, text: str, length_preference: str = "medium") -> dict:
        """
        Summarizes the input text.
        length_preference: "short", "medium", or "long"
        """
        self.load_model()
        
        # Configure min/max token length
        length_params = {
            "short": {"min_length": 30, "max_length": 80},
            "medium": {"min_length": 80, "max_length": 150},
            "long": {"min_length": 150, "max_length": 300}
        }
        
        params = length_params.get(length_preference, length_params["medium"])
        
        # Handle texts longer than model max input by chunking and summarizing each chunk
        max_chars = 3800
        if len(text) > max_chars:
            logger.info(f"Text too long ({len(text)} chars). Chunking for summarization.")
            chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            
            summary_texts = []
            for chunk in chunks:
                word_count = len(chunk.split())
                chunk_min = params["min_length"]
                chunk_max = params["max_length"]
                if word_count < chunk_min:
                    chunk_min = max(5, word_count // 2)
                    chunk_max = min(chunk_max, word_count + 10)
                
                result = self._model(chunk, min_length=chunk_min, max_length=chunk_max, truncation=True)
                summary_texts.append(result[0]['summary_text'])
                
            summary_text = " ".join(summary_texts)
        else:
            word_count = len(text.split())
            if word_count < params["min_length"]:
                params["min_length"] = max(5, word_count // 2)
                params["max_length"] = min(params["max_length"], word_count + 10)
                
            summary_result = self._model(text, min_length=params["min_length"], max_length=params["max_length"], truncation=True)
            summary_text = summary_result[0]['summary_text']
            
        bullets = self.to_bullets(summary_text)
        
        return {
            "summary_paragraph": summary_text,
            "summary_bullets": bullets
        }
        
    def to_bullets(self, text: str) -> list[str]:
        """ Converts a paragraph into bullet points using NLTK sentence tokenization """
        sentences = sent_tokenize(text)
        return sentences

# Singleton instance
summarizer_engine = SummarizerEngine()
