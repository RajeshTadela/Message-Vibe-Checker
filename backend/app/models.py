import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(1000), nullable=False)
    toxicity_score = Column(Float, nullable=False)
    label = Column(String(50), nullable=False) # "Safe", "Caution", "Toxic"
    tone = Column(String(50), nullable=False)
    categories_json = Column(Text, nullable=False) # JSON dictionary of 6 category scores
    char_count = Column(Integer, nullable=False)
    flagged_tokens_json = Column(Text, nullable=False) # JSON array of {token, weight}
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class RewriteRecord(Base):
    __tablename__ = "rewrites"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(String(1000), nullable=False)
    rewritten_text = Column(String(1000), nullable=False)
    mode = Column(String(50), nullable=False) # Constructive, Professional, Friendly, Neutral
    initial_toxicity = Column(Float, nullable=False)
    new_toxicity_score = Column(Float, nullable=False)
    similarity = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class ConversationRecord(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Untitled Conversation")
    raw_text = Column(Text, nullable=False)
    message_count = Column(Integer, default=0)
    avg_toxicity = Column(Float, default=0.0)
    most_toxic_speaker = Column(String(100), default="N/A")
    escalation_trend = Column(String(100), default="Stable (0%)")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    messages = relationship("ConversationMessageRecord", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessageRecord(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    speaker = Column(String(100), nullable=False)
    text = Column(String(1000), nullable=False)
    toxicity_score = Column(Float, nullable=False)
    label = Column(String(50), nullable=False)
    tone = Column(String(50), nullable=False)
    order_index = Column(Integer, default=0)

    conversation = relationship("ConversationRecord", back_populates="messages")

