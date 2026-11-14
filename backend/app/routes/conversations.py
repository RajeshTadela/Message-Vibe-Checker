import re
import numpy as np
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import ConversationRecord, ConversationMessageRecord
from backend.app.schemas import (
    ConversationCreateRequest,
    ConversationSummaryResponse,
    ConversationDetailResponse,
    ConversationMessageSchema
)
from backend.app.services.ml_singleton import get_ml

router = APIRouter(tags=["Conversations"])

def parse_chat_messages(chat_text: str):
    """
    Parses chat lines of format: 'Name: message' or '[Time] Name: message'.
    """
    lines = [line.strip() for line in chat_text.strip().split("\n") if line.strip()]
    parsed = []
    
    line_pattern = re.compile(r"^(?:\[[\d:]+\]\s*)?([A-Za-z0-9_\s\-\.]+?)\s*:\s*(.+)$")

    current_speaker = "User"
    for line in lines:
        match = line_pattern.match(line)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            current_speaker = speaker
            parsed.append((speaker, text))
        else:
            # Continuation line or bare message
            parsed.append((current_speaker, line))

    return parsed

@router.post("/conversations", response_model=ConversationDetailResponse)
def create_conversation(req: ConversationCreateRequest, db: Session = Depends(get_db)):
    chat_text = req.chat_text.strip()
    if not chat_text:
        raise HTTPException(status_code=400, detail="Chat text cannot be empty.")

    parsed_pairs = parse_chat_messages(chat_text)
    if not parsed_pairs:
        raise HTTPException(status_code=400, detail="Could not parse any messages from the provided chat text.")

    ml = get_ml()
    message_records = []
    speaker_scores = {}
    scores_series = []

    for idx, (speaker, text) in enumerate(parsed_pairs):
        # Truncate message text if too long
        truncated_text = text[:1000]
        analysis = ml.toxicity_service.analyze(truncated_text)
        tox_score = analysis["toxicity_score"]
        label = analysis["label"]
        tone = analysis["tone"]

        scores_series.append(tox_score)
        if speaker not in speaker_scores:
            speaker_scores[speaker] = []
        speaker_scores[speaker].append(tox_score)

        msg_rec = ConversationMessageRecord(
            speaker=speaker,
            text=truncated_text,
            toxicity_score=tox_score,
            label=label,
            tone=tone,
            order_index=idx
        )
        message_records.append(msg_rec)

    # Conversation-level stats
    avg_tox = float(np.mean(scores_series)) if scores_series else 0.0

    # Most toxic speaker
    most_toxic_speaker = "N/A"
    highest_speaker_avg = -1.0
    for spk, scores in speaker_scores.items():
        spk_avg = float(np.mean(scores))
        if spk_avg > highest_speaker_avg:
            highest_speaker_avg = spk_avg
            most_toxic_speaker = spk

    # Escalation Trend
    if len(scores_series) >= 2:
        mid = len(scores_series) // 2
        first_half_avg = float(np.mean(scores_series[:mid]))
        second_half_avg = float(np.mean(scores_series[mid:]))
        delta = second_half_avg - first_half_avg
        if delta >= 4.0:
            trend = f"Escalating (+{delta:.1f}%)"
        elif delta <= -4.0:
            trend = f"De-escalating ({delta:.1f}%)"
        else:
            trend = f"Stable ({delta:+.1f}%)"
    else:
        trend = "Stable (0.0%)"

    title = req.title.strip() if req.title and req.title.strip() else f"Chat ({len(parsed_pairs)} messages)"

    conv_rec = ConversationRecord(
        title=title,
        raw_text=chat_text,
        message_count=len(parsed_pairs),
        avg_toxicity=round(avg_tox, 1),
        most_toxic_speaker=most_toxic_speaker,
        escalation_trend=trend
    )
    db.add(conv_rec)
    db.flush()

    for m in message_records:
        m.conversation_id = conv_rec.id
        db.add(m)

    db.commit()
    db.refresh(conv_rec)

    return ConversationDetailResponse(
        id=conv_rec.id,
        title=conv_rec.title,
        raw_text=conv_rec.raw_text,
        message_count=conv_rec.message_count,
        avg_toxicity=conv_rec.avg_toxicity,
        most_toxic_speaker=conv_rec.most_toxic_speaker,
        escalation_trend=conv_rec.escalation_trend,
        created_at=conv_rec.created_at.isoformat(),
        messages=[
            ConversationMessageSchema(
                id=m.id,
                speaker=m.speaker,
                text=m.text,
                toxicity_score=m.toxicity_score,
                label=m.label,
                tone=m.tone,
                order_index=m.order_index
            )
            for m in conv_rec.messages
        ]
    )

@router.get("/conversations", response_model=List[ConversationSummaryResponse])
def list_conversations(db: Session = Depends(get_db)):
    convs = db.query(ConversationRecord).order_by(ConversationRecord.created_at.desc()).all()
    return [
        ConversationSummaryResponse(
            id=c.id,
            title=c.title,
            message_count=c.message_count,
            avg_toxicity=c.avg_toxicity,
            most_toxic_speaker=c.most_toxic_speaker,
            escalation_trend=c.escalation_trend,
            created_at=c.created_at.isoformat()
        )
        for c in convs
    ]

@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
def get_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(ConversationRecord).filter(ConversationRecord.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found.")

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        raw_text=conv.raw_text,
        message_count=conv.message_count,
        avg_toxicity=conv.avg_toxicity,
        most_toxic_speaker=conv.most_toxic_speaker,
        escalation_trend=conv.escalation_trend,
        created_at=conv.created_at.isoformat(),
        messages=[
            ConversationMessageSchema(
                id=m.id,
                speaker=m.speaker,
                text=m.text,
                toxicity_score=m.toxicity_score,
                label=m.label,
                tone=m.tone,
                order_index=m.order_index
            )
            for m in sorted(conv.messages, key=lambda x: x.order_index)
        ]
    )

