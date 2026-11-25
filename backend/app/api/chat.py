from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models import Conversation
from app.schemas import ChatRequest
from app.services.chat_service import list_conversations, send_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/conversations")
async def get_conversations(db: AsyncSession = Depends(get_db)):
    return await list_conversations(db)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/messages")
async def post_message(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    conversation, user_message, assistant_message = await send_message(
        db, payload.message, payload.conversation_id
    )
    return {
        "conversation_id": conversation.id,
        "message": {
            "id": assistant_message.id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at,
        },
    }
