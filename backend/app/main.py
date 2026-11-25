from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.chat import router as chat_router
from app.config import settings
from app.db import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        message_columns = await connection.run_sync(
            lambda sync_connection: {
                column["name"] for column in inspect(sync_connection).get_columns("messages")
            }
        )
        if "profiles" not in message_columns:
            await connection.execute(text("ALTER TABLE messages ADD COLUMN profiles JSON"))
        message_extra_columns = await connection.run_sync(
            lambda sync_connection: {
                column["name"] for column in inspect(sync_connection).get_columns("messages")
            }
        )
        for column, definition in (
            ("criteria", "JSON"),
            ("total", "INTEGER"),
            ("shown", "INTEGER"),
            ("has_more", "INTEGER"),
        ):
            if column not in message_extra_columns:
                await connection.execute(text(f"ALTER TABLE messages ADD COLUMN {column} {definition}"))

        conversation_columns = await connection.run_sync(
            lambda sync_connection: {
                column["name"] for column in inspect(sync_connection).get_columns("conversations")
            }
        )
        if "active_criteria" not in conversation_columns:
            await connection.execute(text("ALTER TABLE conversations ADD COLUMN active_criteria JSON"))
        if "seen_profile_ids" not in conversation_columns:
            await connection.execute(text("ALTER TABLE conversations ADD COLUMN seen_profile_ids JSON"))
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
