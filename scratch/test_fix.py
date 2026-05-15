import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from summarizer import summarizer_engine
import logging

logging.basicConfig(level=logging.INFO)

# A short text (approx 130 words as in the user's case)
short_text = """
The NASA James Webb Space Telescope has captured a stunning new image of a distant galaxy, revealing intricate details never seen before. 
Astronomers say the high-resolution data will help them understand how stars are formed in the early universe. 
The telescope, which was launched in December 2021, has already provided a wealth of information about our cosmos. 
Scientists are particularly excited about the discovery of organic molecules in the atmosphere of a planet orbiting a nearby star. 
This discovery could have significant implications for our search for life beyond Earth. 
The Webb telescope continues to push the boundaries of our knowledge and inspire future generations of scientists. 
In addition to its scientific contributions, the telescope's images have captured the public's imagination, reminding us of the beauty and mystery of the universe. 
The mission is a testament to international cooperation and human ingenuity.
As we look deeper into space, we are also looking back in time, uncovering the history of the universe one image at a time.
"""

print(f"Word count: {len(short_text.split())}")

print("\nSummarizing with 'medium' preference (max_length=150 in config):")
result = summarizer_engine.summarize(short_text, length_preference="medium")

print("\nSummary Results:")
print(result["summary_paragraph"])
