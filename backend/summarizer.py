from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import logging
import re

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
        Summarizes the input text with improved chunking and length management.
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
        
        # Max input for BART-large-cnn is effectively around 800-1000 words.
        # We'll use a safer character limit for chunking.
        max_chunk_chars = 3000 
        
        if len(text) > max_chunk_chars:
            logger.info(f"Article is long ({len(text)} chars). Using multi-stage summarization.")
            # Split by paragraphs to keep context better than hard character slicing
            paragraphs = text.split('\n')
            chunks = []
            current_chunk = ""
            
            for p in paragraphs:
                if len(current_chunk) + len(p) < max_chunk_chars:
                    current_chunk += p + "\n"
                else:
                    if current_chunk: chunks.append(current_chunk.strip())
                    current_chunk = p + "\n"
            if current_chunk: chunks.append(current_chunk.strip())
            
            # Step 1: Summarize each chunk
            intermediate_summaries = []
            for chunk in chunks:
                if len(chunk.split()) < 20: continue # Skip very small chunks
                
                # For intermediate steps, we use medium settings
                res = self._model(chunk, min_length=40, max_length=100, truncation=True)
                intermediate_summaries.append(res[0]['summary_text'])
            
            combined_summary = " ".join(intermediate_summaries)
            
            # Step 2: Final condensation if the combined summary is still too long
            if len(combined_summary.split()) > params["max_length"]:
                logger.info("Condensing combined summaries for final output.")
                final_res = self._model(combined_summary, 
                                      min_length=params["min_length"], 
                                      max_length=params["max_length"], 
                                      truncation=True)
                summary_text = final_res[0]['summary_text']
            else:
                summary_text = combined_summary
        else:
            # Single pass summary
            word_count = len(text.split())
            if word_count < params["min_length"]:
                min_l = max(10, word_count // 2)
                max_l = min(params["max_length"], word_count + 20)
            else:
                min_l = params["min_length"]
                max_l = params["max_length"]
                
            summary_result = self._model(text, min_length=min_l, max_length=max_l, truncation=True)
            summary_text = summary_result[0]['summary_text']
            
        bullets = self.to_bullets(summary_text)
        
        return {
            "summary_paragraph": summary_text,
            "summary_bullets": bullets
        }
        
    def to_bullets(self, text: str) -> list[str]:
        """ Converts a paragraph into structured bullet points with headings """
        sentences = sent_tokenize(text)
        formatted_bullets = []
        
        # Stop words to avoid using as categories
        skip_words = {"THE", "A", "AN", "THIS", "SO", "THESE", "THOSE", "IN", "AT", "ON", "OF"}
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Heuristic: Extract first 1-2 important words as a category
            words = [w for w in re.split(r'\W+', sent) if w]
            category = ""
            for i in range(min(2, len(words))):
                word = words[i].upper()
                if word not in skip_words or i > 0:
                    category += words[i].capitalize() + " "
            
            category = category.strip()
            if category:
                formatted_bullets.append(f"{category}: {sent}")
            else:
                formatted_bullets.append(sent)
                
        return formatted_bullets

# Singleton instance
summarizer_engine = SummarizerEngine()
