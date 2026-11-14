import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.services.ml_singleton import get_ml
from backend.app.routes import health, analyze, rewrite, conversations, insights, samples

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Tone Checker (VibeCheck): Multi-label toxicity analysis, tone detection, and constructive rewriter."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers at root and /api prefix
for prefix in ["", "/api"]:
    app.include_router(health.router, prefix=prefix)
    app.include_router(analyze.router, prefix=prefix)
    app.include_router(rewrite.router, prefix=prefix)
    app.include_router(conversations.router, prefix=prefix)
    app.include_router(insights.router, prefix=prefix)
    app.include_router(samples.router, prefix=prefix)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
