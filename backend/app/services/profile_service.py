import json
import re
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "profiles.json"
with DATA_PATH.open(encoding="utf-8") as data_file:
    _dataset = json.load(data_file)

PROFILES: list[dict] = _dataset["profiles"]

if len(PROFILES) != 500:
    raise ValueError(f"Expected 500 profiles in {DATA_PATH}, found {len(PROFILES)}")
if any(not 21 <= profile["age"] <= 45 for profile in PROFILES):
    raise ValueError(f"Profile ages must be between 21 and 45 in {DATA_PATH}")
if any(profile["gender"] not in {"Male", "Female"} for profile in PROFILES):
    raise ValueError(f"Profiles must use Male or Female gender values in {DATA_PATH}")

_CITIES = sorted({profile["city"] for profile in PROFILES}, key=len, reverse=True)
_CULTURES = sorted({profile["culture_community"] for profile in PROFILES}, key=len, reverse=True)
_REGIONS = sorted({profile["region"] for profile in PROFILES}, key=len, reverse=True)
_LANGUAGES = sorted(
    {language for profile in PROFILES for language in profile["languages"]},
    key=len,
    reverse=True,
)
_INTERESTS = sorted(
    {interest for profile in PROFILES for interest in profile["interests"]},
    key=len,
    reverse=True,
)
_RELIGIONS = sorted(
    {profile["religion"] for profile in PROFILES if profile["religion"] != "Prefer not to say"},
    key=len,
    reverse=True,
)

_PROFESSION_TERMS = {
    "doctor": ("doctor", "physician", "medical"),
    "engineer": ("engineer",),
    "teacher": ("teacher", "educator"),
    "nurse": ("nurse",),
    "designer": ("designer",),
    "lawyer": ("lawyer", "attorney"),
    "architect": ("architect",),
    "analyst": ("analyst",),
    "entrepreneur": ("entrepreneur",),
    "researcher": ("researcher",),
    "chef": ("chef",),
    "journalist": ("journalist",),
    "scientist": ("scientist",),
    "manager": ("manager",),
}
_STOP_WORDS = {
    "a", "an", "and", "are", "around", "at", "between", "city", "communities",
    "community", "find", "fluent", "for", "from", "in", "interested", "interest",
    "interests", "language", "languages", "me", "near", "of", "old", "people",
    "person", "please", "profile", "profiles", "profession", "professional",
    "region", "search", "show", "speak", "speaking", "speakers", "the", "to",
    "with", "aged", "age", "year", "years",
    "someone", "i", "my", "want", "looking", "matches", "match", "help",
    "you", "write", "first", "message", "who", "enjoy", "like", "likes",
    "love", "loves", "their",
}
_GENDER_TERMS = {
    "Female": {"female", "women", "woman", "girl"},
    "Male": {"male", "men", "man", "boy"},
}
_NO_MATCH_REPLY = (
    "I couldn't find profiles matching those details. "
    "Try changing the location, age range, or profession."
)


def _contains_term(text: str, term: str) -> bool:
    return re.search(rf"\b{re.escape(term)}s?\b", text, flags=re.IGNORECASE) is not None


def _matching_terms(query: str, values: list[str]) -> list[str]:
    return [value for value in values if _contains_term(query, value)]


def _age_bounds(query: str) -> tuple[int | None, int | None]:
    range_match = re.search(
        r"\b(?:aged?\s*)?(\d{1,2})\s*(?:to|and|-|–)\s*(\d{1,2})\b",
        query,
        flags=re.IGNORECASE,
    )
    if range_match:
        first, second = map(int, range_match.groups())
        return min(first, second), max(first, second)

    upper_match = re.search(r"\b(?:under|below|younger than)\s+(\d{1,2})\b", query, re.IGNORECASE)
    if upper_match:
        return None, int(upper_match.group(1)) - 1

    lower_match = re.search(r"\b(?:over|above|older than)\s+(\d{1,2})\b", query, re.IGNORECASE)
    if lower_match:
        return int(lower_match.group(1)) + 1, None

    return None, None


def _query_constraints(query: str):
    age_min, age_max = _age_bounds(query)
    gender = None
    if re.search(r"\b(female|women|woman|girls?)\b", query, re.IGNORECASE):
        gender = "Female"
    elif re.search(r"\b(male|men|man|boys?)\b", query, re.IGNORECASE):
        gender = "Male"

    cities = _matching_terms(query, _CITIES)
    language_query = re.search(
        r"\b(?:speaks?|speaking|speakers?|language|fluent)\b",
        query,
        flags=re.IGNORECASE,
    )
    languages = _matching_terms(query, _LANGUAGES) if language_query else []
    cultures = [] if languages else _matching_terms(query, _CULTURES)
    regions = _matching_terms(query, _REGIONS)
    interests = _matching_terms(query, _INTERESTS)
    religions = _matching_terms(query, _RELIGIONS)
    profession_keywords = [
        keywords
        for label, keywords in _PROFESSION_TERMS.items()
        if _contains_term(query, label)
        or any(_contains_term(query, keyword) for keyword in keywords)
    ]

    return {
        "age_min": age_min,
        "age_max": age_max,
        "gender": gender,
        "cities": cities,
        "cultures": cultures,
        "regions": regions,
        "languages": languages,
        "interests": interests,
        "religions": religions,
        "profession_keywords": profession_keywords,
    }


def _matches(profile: dict, constraints: dict) -> bool:
    if constraints["age_min"] is not None and profile["age"] < constraints["age_min"]:
        return False
    if constraints["age_max"] is not None and profile["age"] > constraints["age_max"]:
        return False
    if constraints["gender"] and profile["gender"] != constraints["gender"]:
        return False
    if constraints["cities"] and profile["city"] not in constraints["cities"]:
        return False
    if constraints["cultures"] and profile["culture_community"] not in constraints["cultures"]:
        return False
    if constraints["regions"] and profile["region"] not in constraints["regions"]:
        return False
    if constraints["languages"] and not any(
        language in profile["languages"] for language in constraints["languages"]
    ):
        return False
    if constraints["interests"] and not any(
        interest in profile["interests"] for interest in constraints["interests"]
    ):
        return False
    if constraints["religions"] and profile["religion"] not in constraints["religions"]:
        return False
    if constraints["profession_keywords"]:
        profession = profile["profession"].casefold()
        if not any(
            keyword in profession
            for keywords in constraints["profession_keywords"]
            for keyword in keywords
        ):
            return False
    return True


def _normalize_term(term: str) -> str:
    normalized = term.casefold()
    if len(normalized) > 3 and normalized.endswith("s"):
        normalized = normalized[:-1]
    return normalized


def _search_terms(query: str, constraints: dict) -> set[str]:
    ignored = set(_STOP_WORDS)
    for values in ("cities", "cultures", "regions", "languages", "interests", "religions"):
        for value in constraints[values]:
            ignored.update(value.casefold().split())
    for gender_terms in _GENDER_TERMS.values():
        ignored.update(gender_terms)
    for keywords in constraints["profession_keywords"]:
        ignored.update(keyword.casefold() for keyword in keywords)

    query_terms = set()
    for raw_term in re.findall(r"[a-zA-Z]{3,}", query):
        term = _normalize_term(raw_term)
        if term not in ignored:
            query_terms.add(term)
    return query_terms


def _relevance_score(profile: dict, query_terms: set[str]) -> int:
    searchable_terms = {
        _normalize_term(term)
        for term in re.findall(
            r"[a-zA-Z]{3,}",
            " ".join(
                [
                    profile["profession"],
                    profile["culture_community"],
                    profile["city"],
                    profile["region"],
                    profile["religion"],
                    profile["education"],
                    profile["short_bio"],
                    profile["relationship_preferences"]["relationship_goal"],
                    *profile["languages"],
                    *profile["interests"],
                ]
            ),
        )
    }
    return sum(term in searchable_terms for term in query_terms)


def search_profiles(query: str, limit: int = 5) -> tuple[str, list[dict]]:
    if re.search(r"\bfavorites?\b", query, flags=re.IGNORECASE):
        return (
            "Saved favorites aren't available in this demo yet. Try searching the sample profiles by location, age, or profession.",
            [],
        )

    constraints = _query_constraints(query)
    matching = [profile for profile in PROFILES if _matches(profile, constraints)]
    query_terms = _search_terms(query, constraints)
    scored_matches = [
        (_relevance_score(profile, query_terms), profile)
        for profile in matching
    ]
    if query_terms and not any(score for score, _ in scored_matches):
        return _NO_MATCH_REPLY, []

    scored_matches.sort(
        key=lambda result: (-result[0], result[1]["id"])
    )
    matching = [profile for _, profile in scored_matches]

    if re.search(r"\b(first message|message opener|conversation starter)\b", query, re.IGNORECASE):
        if not matching:
            return (
                "I couldn't find a profile matching those details to write to. Try changing the location or age range.",
                [],
            )
        profile = matching[0]
        interest = profile["interests"][0]
        reply = (
            f"Here's a conversation starter for {profile['name']}, based on their interest in "
            f"{interest}: \"I noticed you enjoy {interest}. What first got you interested in it?\""
        )
        return reply, [profile]

    total = len(matching)
    results = matching[:limit]
    if total == 0:
        reply = _NO_MATCH_REPLY
    else:
        reply = f"I found {total} matching profile{'s' if total != 1 else ''}. Here are up to {len(results)} results."
    return reply, results


def extract_criteria(query: str) -> dict:
    constraints = _query_constraints(query)
    age_min = constraints["age_min"]
    age_max = constraints["age_max"]
    age_clamped = False
    if age_min is not None and age_min < 18:
        age_min = 18
        age_clamped = True
    if age_max is not None and age_max < 18:
        age_max = 18
        age_clamped = True
    if age_min is not None and age_max is not None and age_min > age_max:
        age_min, age_max = age_max, age_min

    gender = constraints["gender"]
    looking_for = "bride" if gender == "Female" else "groom" if gender == "Male" else None
    city = constraints["cities"][0] if constraints["cities"] else None
    region = constraints["regions"][0] if constraints["regions"] else None
    religion = constraints["religions"][0] if constraints["religions"] else None
    profession = None
    if constraints["profession_keywords"]:
        keyword_set = constraints["profession_keywords"][0]
        for label, keywords in _PROFESSION_TERMS.items():
            if keyword_set == keywords:
                profession = label
                break

    unsupported_terms = []
    unsupported_words = (
        ("tall", "height"),
        ("short", "height"),
        ("income", "income"),
        ("education", "education"),
        ("vegetarian", "diet"),
        ("non-vegetarian", "diet"),
    )
    lowered = query.casefold()
    for term, field_name in unsupported_words:
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            unsupported_terms.append(field_name)

    needs_clarification = not any(
        (
            age_min,
            age_max,
            city,
            region,
            religion,
            profession,
            constraints["languages"],
            constraints["interests"],
            gender,
        )
    )
    return {
        "looking_for": looking_for,
        "age_min": age_min,
        "age_max": age_max,
        "country": "India" if city or region or religion or profession or gender else None,
        "state": region,
        "city": city,
        "religion": religion,
        "mother_tongue": constraints["languages"][0] if constraints["languages"] else None,
        "profession": profession,
        "diet": None,
        "needs_clarification": needs_clarification,
        "clarifying_question": "Happy to help. Which age range and city should I look in?" if needs_clarification else None,
        "unsupported_terms": sorted(set(unsupported_terms)),
        "age_clamped": age_clamped,
    }


def card_payload(profile: dict) -> dict:
    first_name = profile["name"].split()[0]
    return {
        "profile_id": profile["id"],
        "first_name": first_name,
        "age": profile["age"],
        "city": profile["city"],
        "profession": profile["profession"].split(" / ")[0],
        "photo_url": None,
        "profile_url": f"/profile/{profile['id']}",
    }


def search_profiles_page(
    query: str,
    seen_profile_ids: list[str] | None = None,
    limit: int = 5,
):
    seen = set(seen_profile_ids or [])
    if re.search(r"\bfavorites?\b", query, flags=re.IGNORECASE):
        return {
            "reply": "Saved favorites aren't available in this demo yet.",
            "criteria": None,
            "total": 0,
            "cards": [],
            "has_more": False,
        }

    criteria = extract_criteria(query)
    if criteria["needs_clarification"]:
        return {
            "reply": criteria["clarifying_question"],
            "criteria": criteria,
            "total": 0,
            "cards": [],
            "has_more": False,
        }

    _, matches = search_profiles(query, limit=500)
    matches = [profile for profile in matches if profile["id"] not in seen]
    total = len(matches)
    cards = [card_payload(profile) for profile in matches[:limit]]
    if total == 0:
        reply = "I couldn't find a match for that. You could try a wider age range or nearby cities."
    elif len(matches) > limit:
        reply = f"I found {total} profiles. Here are the first {limit}."
    else:
        reply = f"I found {total} matching profile{'s' if total != 1 else ''}."
    if cards:
        understood = criteria_summary(criteria)
        reply = understood + " " + reply
    if criteria["age_clamped"]:
        reply = "Members have to be 18 or older, so I searched from 18. " + reply
    if criteria["unsupported_terms"]:
        reply += " I can't search on that, but I can use things like age, location, religion, mother tongue, and profession."
    return {
        "reply": reply,
        "criteria": criteria,
        "total": total,
        "cards": cards,
        "has_more": total > len(cards),
    }


def criteria_summary(criteria: dict) -> str:
    parts = []
    if criteria["looking_for"]:
        parts.append(criteria["looking_for"] + "s")
    if criteria["age_min"] is not None or criteria["age_max"] is not None:
        if criteria["age_min"] is not None and criteria["age_max"] is not None:
            parts.append(f"aged {criteria['age_min']} to {criteria['age_max']}")
        elif criteria["age_min"] is not None:
            parts.append(f"aged {criteria['age_min']} or older")
        else:
            parts.append(f"aged {criteria['age_max']} or younger")
    if criteria["city"]:
        parts.append(f"in {criteria['city']}")
    elif criteria["state"]:
        parts.append(f"in {criteria['state']}")
    if criteria["religion"]:
        parts.append(f"who are {criteria['religion'].lower()}")
    if criteria["mother_tongue"]:
        parts.append(f"who speak {criteria['mother_tongue']}")
    if criteria["profession"]:
        parts.append(f"working as {criteria['profession']}s")
    if not parts:
        return "Here's what I looked for."
    return "Here's what I looked for: " + ", ".join(parts) + "."
