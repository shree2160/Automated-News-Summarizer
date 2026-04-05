import logging
import sys
import os

# Add the backend directory to the path so we can import models
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "backend")))

from summarizer import summarizer_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test():
    test_text = """
    The BBC is a British public service broadcaster. Its main headquarters is at Broadcasting House in Portland Place, London. 
    It is the world's oldest national broadcaster, and the largest broadcaster in the world by number of employees.
    It employs over 22,000 staff in total, of whom approximately 19,000 are in public-sector broadcasting.
    """
    
    print("\n--- Starting Summarization Test ---")
    try:
        print("Loading Model...")
        summarizer_engine.load_model()
        print("Model Loaded Successfully!")
        
        print("\nSummarizing...")
        result = summarizer_engine.summarize(test_text, "short")
        print("\nResult obtained:")
        print(f"Summary Paragraph: {result['summary_paragraph']}")
        print(f"Summary Bullets: {result['summary_bullets']}")
        
    except Exception as e:
        print(f"\n[ERROR] Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
