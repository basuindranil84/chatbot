from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    active_criteria: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    seen_profile_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="(Message.created_at, Message.id)",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    profiles: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    criteria: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shown: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_more: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class SearchAudit(Base):
    __tablename__ = "assistant_search_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[str] = mapped_column(String(100), default="demo-member")
    action: Mapped[str] = mapped_column(String(20), default="search")
    criteria: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
