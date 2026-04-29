from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class TenantSchema(BaseModel):
    tenant_id: str
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TenantCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserSchema(BaseModel):
    user_id: str
    tenant_id: str
    email: EmailStr
    name: str
    password_hash: str = ""
    role: str = "user"  # "user" or "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str
    password: str
    tenant_id: str

class InterestSchema(BaseModel):
    interest_id: str
    user_id: str
    keywords: List[str]
    categories: List[str]

class NewsItemSchema(BaseModel):
    news_id: str
    title: str
    content: str
    source: str
    link: str = ""
    published_at: datetime
    category: str
    embedding_id: Optional[str] = None

class TriggerSchema(BaseModel):
    trigger_id: str
    user_id: str
    news_id: str
    score: float
    sent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatHistorySchema(BaseModel):
    chat_id: str
    user_id: str
    query: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
