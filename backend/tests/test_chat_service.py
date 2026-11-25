import unittest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.models import Base, Conversation
from app.services.chat_service import send_message


class ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_profile_results_are_returned_and_persisted_for_resume(self):
        async with self.session_factory() as session:
            conversation, _, assistant_message = await send_message(
                session,
                "Find doctors in Kolkata aged 28 to 32",
                None,
            )
            conversation_id = conversation.id
            self.assertEqual(1, len(assistant_message.profiles))

            result = await session.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.messages))
            )
            restored = result.scalar_one()

        restored_assistant_message = next(
            message for message in restored.messages if message.role == "assistant"
        )
        self.assertEqual(1, len(restored_assistant_message.profiles))
        self.assertEqual("Kolkata", restored_assistant_message.profiles[0]["city"])


if __name__ == "__main__":
    unittest.main()
