import json
import numpy as np
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AnalysisRecord, RewriteRecord, ConversationMessageRecord
from backend.app.schemas import InsightsResponse, ToxicityPoint, FlaggedWordStat

router = APIRouter(tags=["Insights"])

@router.get("/insights", response_model=InsightsResponse)
def get_insights(db: Session = Depends(get_db)):
    analyses = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.asc()).all()
    rewrites = db.query(RewriteRecord).all()
    conv_messages = db.query(ConversationMessageRecord).all()

    total_analyzed = len(analyses) + len(conv_messages)
    
    # Calculate toxicity scores
    all_scores = [a.toxicity_score for a in analyses] + [m.toxicity_score for m in conv_messages]
    avg_toxicity = float(round(np.mean(all_scores), 1)) if all_scores else 0.0

    # Category distribution averages
    cat_accum = {
        "toxic": [],
        "insult": [],
        "harassment": [],
        "obscene": [],
        "threat": [],
        "identity_attack": []
    }
    for a in analyses:
        try:
            c_dict = json.loads(a.categories_json)
            for k in cat_accum:
                if k in c_dict:
                    cat_accum[k].append(c_dict[k])
        except Exception:
            pass

    category_distribution = {
        k: float(round(np.mean(v), 1)) if v else 0.0
        for k, v in cat_accum.items()
    }

    # Tone distribution
    tone_counts = Counter()
    for a in analyses:
        if a.tone:
            tone_counts[a.tone] += 1
    for m in conv_messages:
        if m.tone:
            tone_counts[m.tone] += 1

    tone_distribution = dict(tone_counts)
    if not tone_distribution:
        tone_distribution = {"Neutral": 0, "Polite": 0, "Friendly": 0, "Rude": 0, "Aggressive": 0, "Sarcastic-ish/Passive-aggressive": 0}

    # Toxicity timeline (analyses points)
    toxicity_over_time = [
        ToxicityPoint(
            timestamp=a.created_at.strftime("%H:%M:%S"),
            toxicity_score=a.toxicity_score,
            label=a.label
        )
        for a in analyses[-30:] # return up to last 30 for clear chart
    ]

    # Top flagged words
    word_counter = Counter()
    for a in analyses:
        try:
            tokens = json.loads(a.flagged_tokens_json)
            for item in tokens:
                token_word = item.get("token", "").lower()
                if token_word and len(token_word) > 1:
                    word_counter[token_word] += 1
        except Exception:
            pass

    top_flagged_words = [
        FlaggedWordStat(word=w, count=cnt)
        for w, cnt in word_counter.most_common(10)
    ]

    # Rewrites metrics
    total_rewrites = len(rewrites)
    if rewrites:
        improvements = [max(0.0, r.initial_toxicity - r.new_toxicity_score) for r in rewrites]
        rewrite_improvement_avg = float(round(np.mean(improvements), 1))
    else:
        rewrite_improvement_avg = 0.0

    return InsightsResponse(
        total_analyzed=total_analyzed,
        avg_toxicity=avg_toxicity,
        category_distribution=category_distribution,
        tone_distribution=tone_distribution,
        toxicity_over_time=toxicity_over_time,
        top_flagged_words=top_flagged_words,
        rewrite_improvement_avg=rewrite_improvement_avg,
        total_rewrites=total_rewrites
    )

