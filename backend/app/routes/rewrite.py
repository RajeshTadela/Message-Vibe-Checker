from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import RewriteRecord
from backend.app.schemas import RewriteRequest, RewriteResponse
from backend.app.services.ml_singleton import get_ml

router = APIRouter(tags=["Rewrite"])

@router.post("/rewrite", response_model=RewriteResponse)
def rewrite_message(req: RewriteRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text exceeds maximum length of 1000 characters.")

    valid_modes = ["Constructive", "Professional", "Friendly", "Neutral"]
    mode = req.mode.capitalize()
    if mode not in valid_modes:
        mode = "Constructive"

    ml = get_ml()
    scorer = lambda txt: ml.toxicity_service.analyze(txt)["toxicity_score"] / 100.0

    # Get initial toxicity for record keeping
    initial_analysis = ml.toxicity_service.analyze(text)
    initial_tox = initial_analysis["toxicity_score"]

    res = ml.rewriter_engine.rewrite(text, mode=mode, toxicity_scorer=scorer)

    # Persist in SQLite
    try:
        record = RewriteRecord(
            original_text=text,
            rewritten_text=res["rewrite"],
            mode=res["mode"],
            initial_toxicity=initial_tox,
            new_toxicity_score=round(res["new_toxicity_score"] * 100.0, 1),
            similarity=res["similarity"]
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning: Failed to save rewrite record: {e}")

    return RewriteResponse(
        original=res["original"],
        rewrite=res["rewrite"],
        mode=res["mode"],
        new_toxicity_score=round(res["new_toxicity_score"] * 100.0, 1),
        similarity=res["similarity"]
    )

