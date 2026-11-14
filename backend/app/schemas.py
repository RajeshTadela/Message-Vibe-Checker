from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# Analyze Schemas
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Message text to analyze (max 1000 chars)")

class CategoryScores(BaseModel):
    toxic: float
    insult: float
    harassment: float
    obscene: float
    threat: float
    identity_attack: float

class FlaggedToken(BaseModel):
    token: str
    weight: float

class AnalyzeResponse(BaseModel):
    toxicity_score: float
    label: str # "Safe" | "Caution" | "Toxic"
    tone: str
    categories: CategoryScores
    char_count: int
    flagged_tokens: List[FlaggedToken]
    explanation: Optional[str] = None

# Rewrite Schemas
class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    mode: str = Field(default="Constructive", description="Mode: Constructive, Professional, Friendly, Neutral")

class RewriteResponse(BaseModel):
    original: str
    rewrite: str
    mode: str
    new_toxicity_score: float
    similarity: float

# Conversation Schemas
class ConversationMessageSchema(BaseModel):
    id: Optional[int] = None
    speaker: str
    text: str
    toxicity_score: float
    label: str
    tone: str
    order_index: int

class ConversationCreateRequest(BaseModel):
    chat_text: str = Field(..., min_length=1, description="Chat text formatted with 'Speaker: message' lines")
    title: Optional[str] = None

class ConversationSummaryResponse(BaseModel):
    id: int
    title: str
    message_count: int
    avg_toxicity: float
    most_toxic_speaker: str
    escalation_trend: str
    created_at: str

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    raw_text: str
    message_count: int
    avg_toxicity: float
    most_toxic_speaker: str
    escalation_trend: str
    created_at: str
    messages: List[ConversationMessageSchema]

# Insights Schemas
class ToxicityPoint(BaseModel):
    timestamp: str
    toxicity_score: float
    label: str

class FlaggedWordStat(BaseModel):
    word: str
    count: int

class InsightsResponse(BaseModel):
    total_analyzed: int
    avg_toxicity: float
    category_distribution: Dict[str, float]
    tone_distribution: Dict[str, int]
    toxicity_over_time: List[ToxicityPoint]
    top_flagged_words: List[FlaggedWordStat]
    rewrite_improvement_avg: float
    total_rewrites: int

# Sample Schema
class SampleItem(BaseModel):
    id: str
    title: str
    category: str
    text: str
    expected_tone: str
    expected_label: str

