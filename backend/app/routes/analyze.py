import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AnalysisRecord
from backend.app.schemas import AnalyzeRequest, AnalyzeResponse, CategoryScores, FlaggedToken
from backend.app.services.ml_singleton import get_ml

router = APIRouter(tags=["Analyze"])

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_message(req: AnalyzeRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text exceeds maximum length of 1000 characters.")

    ml = get_ml()
    res = ml.toxicity_service.analyze(text)

    # Persist in SQLite
    try:
        record = AnalysisRecord(
            text=text,
            toxicity_score=res["toxicity_score"],
            label=res["label"],
            tone=res["tone"],
            categories_json=json.dumps(res["categories"]),
            char_count=res["char_count"],
            flagged_tokens_json=json.dumps(res["flagged_tokens"]),
            explanation=res.get("explanation", "")
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning: Failed to save analysis record to DB: {e}")

    return AnalyzeResponse(
        toxicity_score=res["toxicity_score"],
        label=res["label"],
        tone=res["tone"],
        categories=CategoryScores(**res["categories"]),
        char_count=res["char_count"],
        flagged_tokens=[FlaggedToken(**t) for t in res["flagged_tokens"]],
        explanation=res.get("explanation")
    )

