from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas.api_models import SummarizeRequest, SummarizeResponse
from .services.scraper import ScraperService, ParserService
from .services.nlp import NLPService
import time

app = FastAPI(
    title="Automated News Summarizer API",
    description="API for extracting and summarizing news articles using AI.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NLP service (singleton-like instance)
# Note: In a production app, you might want to load this differently
nlp_service = NLPService()

@app.get("/")
async def root():
    return {"message": "Welcome to the News Summarizer API. Use /api/v1/summarize (POST) to get started."}

@app.post("/api/v1/summarize", response_model=SummarizeResponse)
async def summarize_article(request: SummarizeRequest):
    try:
        # 1. Fetch HTML
        html_content = ScraperService.fetch_html(request.url)
        
        # 2. Parse Content and Metadata
        article_text = ParserService.extract_text(html_content)
        metadata = ParserService.extract_metadata(html_content)
        
        # 3. Generate Summary
        summary_data = nlp_service.generate_summary(article_text, request.length, metadata.get("title", ""))
        
        # 4. Analyze Sentiment
        sentiment_data = nlp_service.analyze_sentiment(article_text)
        
        # 5. Build Response
        response = SummarizeResponse(
            metadata=metadata,
            summary_paragraph=summary_data["paragraph"],
            summary_bullets=summary_data["bullets"],
            sentiment=sentiment_data,
            original_length=len(article_text),
            summary_length=len(summary_data["paragraph"])
        )
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
