from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: int | None = None


class ProfileResponse(ORMModel):
    id: str
    name: str
    gender: str
    age: int
    city: str
    region: str
    culture_community: str
    languages: list[str]
    religion: str
    profession: str
    education: str
    interests: list[str]
    short_bio: str
    relationship_preferences: dict[str, Any]


class MessageResponse(ORMModel):
    id: int
    role: str
    content: str
    created_at: datetime
    profiles: list[ProfileResponse] | None = None


class ConversationResponse(ORMModel):
    id: int
    title: str
    messages: list[MessageResponse] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
