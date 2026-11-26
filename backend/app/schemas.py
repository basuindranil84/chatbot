from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    conversation_id: int | None = None


class ProfileResponse(ORMModel):
    id: str | None = None
    name: str | None = None
    gender: str | None = None
    age: int
    city: str | None = None
    region: str | None = None
    culture_community: str | None = None
    languages: list[str] | None = None
    religion: str | None = None
    profession: str | None = None
    education: str | None = None
    interests: list[str] | None = None
    short_bio: str | None = None
    relationship_preferences: dict[str, Any] | None = None
    profile_id: str | None = None
    first_name: str | None = None
    photo_url: str | None = None
    profile_url: str | None = None


class MessageResponse(ORMModel):
    id: int
    role: str
    content: str
    created_at: datetime
    profiles: list[ProfileResponse] | None = None
    criteria: dict[str, Any] | None = None
    total: int | None = None
    shown: int | None = None
    has_more: bool | None = None


class ConversationResponse(ORMModel):
    id: int
    title: str
    messages: list[MessageResponse] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
