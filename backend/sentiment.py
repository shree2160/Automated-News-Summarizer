from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self._model = None
        self._model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        
    def load_model(self):
        if self._model is None:
            logger.info("Loading sentiment analysis model...")
            self._model = pipeline("sentiment-analysis", model=self._model_name)
            logger.info("Sentiment model loaded.")
            
    def analyze(self, text: str) -> dict:
        self.load_model()
        # Ensure we don't exceed max token size for Bert (512 tokens)
        truncated_text = text[:1500] 
        result = self._model(truncated_text)[0]
        label = result['label']
        score = result['score']
        return {
            "label": label,
            "score": round(score, 4)
        }

# Singleton instance
analyzer = SentimentAnalyzer()
