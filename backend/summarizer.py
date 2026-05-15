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
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            # Explicitly load tokenizer and model to ensure max_length is correctly set
            tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self._model_name)
            
            # Force set model_max_length if it's missing or too large
            if not hasattr(tokenizer, 'model_max_length') or tokenizer.model_max_length > 1024:
                tokenizer.model_max_length = 1024
            
            self._model = pipeline(
                "summarization", 
                model=model, 
                tokenizer=tokenizer,
                device=-1  # Force CPU to avoid hidden CUDA issues on Windows if not configured
            )
            
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
        
        # BART-large-cnn max position is 1024 tokens.
        # 3000 chars is roughly 600-800 tokens. 
        # If a single chunk is still too long, truncation=True will now work.
        max_chunk_chars = 2500 
        
        if len(text) > max_chunk_chars:
            logger.info(f"Article is long ({len(text)} chars). Using multi-stage summarization.")
            # Split by paragraphs
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            chunks = []
            current_chunk = ""
            
            for p in paragraphs:
                # If adding this paragraph exceeds limit, push current chunk and start new one
                if len(current_chunk) + len(p) < max_chunk_chars:
                    current_chunk += p + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # If the paragraph itself is longer than max_chunk_chars, we must slice it
                    if len(p) > max_chunk_chars:
                        for i in range(0, len(p), max_chunk_chars):
                            chunks.append(p[i:i+max_chunk_chars])
                        current_chunk = ""
                    else:
                        current_chunk = p + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Step 1: Summarize each chunk
            intermediate_summaries = []
            for chunk in chunks:
                if len(chunk.split()) < 30: continue 
                
                try:
                    # Use a smaller max_length for intermediate chunks to keep it manageable
                    res = self._model(chunk, min_length=40, max_length=120, truncation=True)
                    intermediate_summaries.append(res[0]['summary_text'])
                except Exception as e:
                    logger.warning(f"Error summarizing chunk: {str(e)}")
                    continue
            
            if not intermediate_summaries:
                # Fallback if all chunks failed or were too small
                combined_summary = text[:max_chunk_chars]
            else:
                combined_summary = " ".join(intermediate_summaries)
            
            # Step 2: Final condensation if the combined summary is still too long
            # BART has 1024 token limit, so combined_summary shouldn't exceed that if we want a single pass
            # If combined_summary is > 4000 chars, it might still exceed 1024 tokens.
            if len(combined_summary) > max_chunk_chars:
                combined_summary = combined_summary[:max_chunk_chars]

            try:
                final_res = self._model(combined_summary, 
                                      min_length=params["min_length"], 
                                      max_length=params["max_length"], 
                                      truncation=True)
                summary_text = final_res[0]['summary_text']
            except Exception as e:
                logger.error(f"Error in final condensation: {str(e)}")
                summary_text = combined_summary[:500] # Very crude fallback
        else:
            # Single pass summary
            word_count = len(text.split())
            min_l = min(params["min_length"], max(10, word_count // 2))
            max_l = min(params["max_length"], word_count + 20)
            
            # Ensure min_l < max_l
            if min_l >= max_l:
                min_l = max_l // 2

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
