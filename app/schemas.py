from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    kind: str
    role: Optional[str] = None
    full_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None

class MessageOut(BaseModel):
    id: int
    sender: str
    text: str
    intent_matched: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: datetime
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    intent_matched: Optional[str] = None
    confidence_score: Optional[float] = None
    out_of_scope: bool = False
    entities: dict = {}

class ConversationOut(BaseModel):
    id: int
    title: Optional[str] = None
    started_at: datetime
    class Config:
        from_attributes = True

class ConversationDetail(BaseModel):
    id: int
    title: Optional[str] = None
    messages: List[MessageOut] = []