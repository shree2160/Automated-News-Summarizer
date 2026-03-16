from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from scraper import fetch_article
from parser import parse_html
from summarizer import summarizer_engine
from sentiment import analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Automated News Summarizer API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    url: str
    length: str = "medium"

class Metadata(BaseModel):
    title: str
    author: str
    date: str

class Sentiment(BaseModel):
    label: str
    score: float

class SummarizeResponse(BaseModel):
    metadata: Metadata
    summary_paragraph: str
    summary_bullets: list[str]
    sentiment: Sentiment
    original_length: int
    summary_length: int

@app.get("/")
def root_endpoint():
    return {"message": "Automated News Summarizer API is running. Go to /docs for Swagger UI."}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/summarize", response_model=SummarizeResponse)
def summarize_endpoint(req: SummarizeRequest):
    logger.info(f"Received summarize request for URL: {req.url} with length: {req.length}")
    
    # 1. Scrape
    try:
        html_content = fetch_article(req.url)
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    # 2. Parse
    parsed_data = parse_html(html_content)
    article_text = parsed_data.get("text", "")
    
    if not article_text or len(article_text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Article content too short or inaccessible.")
        
    original_length = len(article_text.split())
    
    # 3. Summarize
    try:
        summary_info = summarizer_engine.summarize(article_text, req.length)
    except Exception as e:
        logger.error(f"Summarizer error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate summary.")
        
    # 4. Sentiment
    try:
        sentiment_info = analyzer.analyze(summary_info["summary_paragraph"])
    except Exception as e:
        logger.error(f"Sentiment error: {str(e)}")
        sentiment_info = {"label": "UNKNOWN", "score": 0.0}
        
    summary_length = len(summary_info["summary_paragraph"].split())
    
    return SummarizeResponse(
        metadata=Metadata(
            title=parsed_data.get("title", "Unknown"),
            author=parsed_data.get("author", "Unknown"),
            date=parsed_data.get("date", "Unknown")
        ),
        summary_paragraph=summary_info["summary_paragraph"],
        summary_bullets=summary_info["summary_bullets"],
        sentiment=Sentiment(
            label=sentiment_info["label"],
            score=sentiment_info["score"]
        ),
        original_length=original_length,
        summary_length=summary_length
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
