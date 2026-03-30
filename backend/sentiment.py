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
        
        # Heuristic for neutral: if the confidence for POS/NEG is low, call it NEUTRAL
        # This is a common way to squeeze 3-class sentiment out of binary models
        if score < 0.75:
            final_label = "NEUTRAL"
        else:
            final_label = label
            
        return {
            "label": final_label.upper(),
            "score": round(score, 4)
        }

# Singleton instance
analyzer = SentimentAnalyzer()
