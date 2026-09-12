from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    conversations = relationship("Conversation", back_populates="user")

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="content_editor")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(64), nullable=True, index=True)
    title = Column(String(200), nullable=True)
    language_used = Column(String(10), nullable=True)
    channel = Column(String(10), nullable=False, default="web")
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.id")
    __table_args__ = (Index("ix_conv_user", "user_id"),)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    intent_matched = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(30), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer_en = Column(Text, nullable=False)
    answer_fil = Column(Text, nullable=False)
    last_updated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    last_updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    intents = relationship("Intent", back_populates="kb_entry")

class Intent(Base):
    __tablename__ = "intents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    sample_utterances = Column(Text, nullable=False)
    kb_entry_id = Column(Integer, ForeignKey("knowledge_base.id"), nullable=False)
    kb_entry = relationship("KnowledgeBase", back_populates="intents")