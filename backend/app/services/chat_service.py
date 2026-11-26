import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message, SearchAudit
from app.services.profile_service import search_profiles_page

_SEARCH_TIMES: dict[int, list[float]] = {}
SEARCH_RATE_LIMIT = 10
SEARCH_WINDOW_SECONDS = 60


def _is_rate_limited(conversation_id: int) -> bool:
    now = time.monotonic()
    recent = [sent_at for sent_at in _SEARCH_TIMES.get(conversation_id, []) if now - sent_at < SEARCH_WINDOW_SECONDS]
    if len(recent) >= SEARCH_RATE_LIMIT:
        _SEARCH_TIMES[conversation_id] = recent
        return True
    recent.append(now)
    _SEARCH_TIMES[conversation_id] = recent
    return False


def _criteria_query(criteria: dict | None) -> str:
    if not criteria:
        return ""
    terms = []
    if criteria.get("looking_for") == "bride":
        terms.append("women")
    elif criteria.get("looking_for") == "groom":
        terms.append("men")
    if criteria.get("age_min") is not None or criteria.get("age_max") is not None:
        terms.append(f"aged {criteria.get('age_min') or 18} to {criteria.get('age_max') or 45}")
    if criteria.get("city"):
        terms.append(f"in {criteria['city']}")
    elif criteria.get("state"):
        terms.append(f"in {criteria['state']}")
    if criteria.get("religion"):
        terms.append(criteria["religion"])
    if criteria.get("mother_tongue"):
        terms.append(f"speaking {criteria['mother_tongue']}")
    if criteria.get("profession"):
        terms.append(f"{criteria['profession']}s")
    if criteria.get("height_min_cm") is not None and criteria.get("height_max_cm") is not None:
        terms.append(
            f"{criteria['height_min_cm']} to {criteria['height_max_cm']} cm"
        )
    elif criteria.get("height_min_cm") is not None:
        terms.append(f"at least {criteria['height_min_cm']} cm")
    elif criteria.get("height_max_cm") is not None:
        terms.append(f"under {criteria['height_max_cm']} cm")
    if criteria.get("caste"):
        terms.append(criteria["caste"])
    if criteria.get("gotra"):
        terms.append(criteria["gotra"])
    if criteria.get("diet"):
        terms.append(criteria["diet"])
    if criteria.get("smoking") == ["non-smoker"]:
        terms.append("non-smoker")
    elif criteria.get("smoking"):
        terms.append("smoker")
    if criteria.get("social_drinking"):
        terms.append("social drinker")
    if criteria.get("lifestyle"):
        terms.append(criteria["lifestyle"])
    terms.extend(criteria.get("hobbies", []))
    return " ".join(terms)


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

    if _is_rate_limited(conversation.id):
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=message,
        )
        db.add(user_message)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="You're searching quickly. Please try again in a minute.",
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(user_message)
        await db.refresh(assistant_message)
        await db.refresh(conversation)
        return conversation, user_message, assistant_message

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )
    db.add(user_message)

    seen_profile_ids = list(conversation.seen_profile_ids or [])
    show_more = message.strip().casefold() in {"show more", "show 5 more", "next 5"}
    search_query = _criteria_query(conversation.active_criteria) if show_more and conversation.active_criteria else message
    page = search_profiles_page(search_query, seen_profile_ids=seen_profile_ids, limit=5)
    profiles = page["cards"]
    reply = page["reply"]
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
        profiles=profiles,
        criteria=page["criteria"],
        total=page["total"],
        shown=len(profiles),
        has_more=page["has_more"],
    )
    db.add(assistant_message)
    for card in profiles:
        profile_id = card["profile_id"]
        if profile_id not in seen_profile_ids:
            seen_profile_ids.append(profile_id)
    conversation.seen_profile_ids = seen_profile_ids
    if page["criteria"] is not None:
        conversation.active_criteria = page["criteria"]
    db.add(SearchAudit(
        member_id="demo-member",
        action="search",
        criteria=page["criteria"],
        result_count=page["total"],
    ))
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
