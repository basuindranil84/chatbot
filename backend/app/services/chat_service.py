from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message
from app.services.profile_service import search_profiles


async def send_message(db: AsyncSession, message: str, conversation_id: int | None):
    if conversation_id is None:
        conversation = Conversation(title=message[:60])
        db.add(conversation)
        await db.flush()
    else:
        conversation = await db.get(Conversation, conversation_id)
        if conversation is None:
            conversation = Conversation(title=message[:60])
            db.add(conversation)
            await db.flush()

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )
    db.add(user_message)

    reply, profiles = search_profiles(message)
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
        profiles=profiles,
    )
    db.add(assistant_message)
    await db.commit()

    await db.refresh(user_message)
    await db.refresh(assistant_message)
    await db.refresh(conversation)
    return conversation, user_message, assistant_message


async def list_conversations(db: AsyncSession):
    result = await db.execute(
        select(Conversation).order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()
