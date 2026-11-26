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
_COUNTRIES = sorted({profile["country"] for profile in PROFILES}, key=len, reverse=True)
_CASTES = sorted({profile["caste"] for profile in PROFILES}, key=len, reverse=True)
_GOTRAS = sorted({profile["gotra"] for profile in PROFILES}, key=len, reverse=True)
_DIETS = sorted({profile["diet"] for profile in PROFILES}, key=len, reverse=True)
_SMOKING_OPTIONS = sorted({profile["smoking"] for profile in PROFILES}, key=len, reverse=True)
_SOCIAL_DRINKING_OPTIONS = sorted(
    {profile["social_drinking"] for profile in PROFILES},
    key=len,
    reverse=True,
)
_LIFESTYLES = sorted({profile["lifestyle"] for profile in PROFILES}, key=len, reverse=True)
_MOTHER_TONGUES = sorted(
    {profile["mother_tongue"] for profile in PROFILES},
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
        r"\b(?:speaks?|speaking|speakers?|language|fluent|mother\s+tongue)\b",
        query,
        flags=re.IGNORECASE,
    )
    languages = _matching_terms(query, _MOTHER_TONGUES) if language_query else []
    cultures = [] if languages else _matching_terms(query, _CULTURES)
    regions = _matching_terms(query, _REGIONS)
    interests = _matching_terms(query, _INTERESTS)
    religions = _matching_terms(query, _RELIGIONS)
    countries = _matching_terms(query, _COUNTRIES)
    location_match = re.search(r"\b(?:in|near|around)\s+([A-Za-z][A-Za-z-]+)\b", query)
    known_location_words = {
        _normalize_term(word)
        for value in _CITIES + _REGIONS + _COUNTRIES
        for word in re.findall(r"[a-zA-Z]+", value)
    }
    unknown_locations = []
    if location_match:
        location_word = location_match.group(1)
        if (
            location_word[0].isupper()
            and _normalize_term(location_word) not in known_location_words
            and location_word.casefold() not in {"me", "city", "state"}
        ):
            unknown_locations.append(location_word)
    castes = _matching_terms(query, _CASTES)
    gotras = _matching_terms(query, _GOTRAS)
    diets = _matching_terms(query, _DIETS)
    lifestyles = _matching_terms(query, _LIFESTYLES)

    height_range = re.search(
        r"\b(\d{3})\s*(?:to|and|-|–)\s*(\d{3})\s*(?:cm|centimeters?)\b",
        query,
        flags=re.IGNORECASE,
    )
    height_min_match = re.search(
        r"\b(?:at least|minimum|min|over|above|taller than|height of)\s*(\d{3})\s*(?:cm|centimeters?)?\b",
        query,
        flags=re.IGNORECASE,
    )
    height_max_match = re.search(
        r"\b(?:under|below|up to|at most|maximum|max|shorter than)\s*(\d{3})\s*(?:cm|centimeters?)?\b",
        query,
        flags=re.IGNORECASE,
    )
    height_cm_match = re.search(r"\b(\d{3})\s*(?:cm|centimeters?)\b", query, flags=re.IGNORECASE)
    height_min_cm = None
    height_max_cm = None
    if height_range:
        first, second = map(int, height_range.groups())
        height_min_cm, height_max_cm = min(first, second), max(first, second)
    elif height_min_match or height_cm_match:
        height_min_cm = int((height_min_match or height_cm_match).group(1))
    elif height_max_match:
        height_max_cm = int(height_max_match.group(1))
    height_requested = bool(re.search(r"\b(?:tall|height)\b", query, re.IGNORECASE))
    height_values = [value for value in (height_min_cm, height_max_cm) if value is not None]
    invalid_height = any(not 100 <= value <= 250 for value in height_values)
    height_needs_clarification = invalid_height or (
        height_requested and height_min_cm is None and height_max_cm is None
    )

    smoking = _matching_terms(query, _SMOKING_OPTIONS)
    if re.search(r"\bnon[- ]?smok(?:ers?|ing)\b", query, re.IGNORECASE):
        smoking = ["non-smoker"]
    elif re.search(r"\bsmok(?:ers?|ing)\b", query, re.IGNORECASE) and not smoking:
        smoking = ["occasional", "regular"]

    social_drinking = []
    if re.search(r"\b(?:no|non)[- ]?social\s+drink(?:ers?|ing)\b", query, re.IGNORECASE):
        social_drinking = ["none"]
    elif re.search(r"\bsocial\s+drink(?:ers?|ing)\b", query, re.IGNORECASE):
        social_drinking = ["occasional", "regular"]
    else:
        social_drinking = _matching_terms(query, _SOCIAL_DRINKING_OPTIONS)

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
        "countries": countries,
        "unknown_locations": unknown_locations,
        "castes": castes,
        "gotras": gotras,
        "diets": diets,
        "smoking": smoking,
        "social_drinking": social_drinking,
        "lifestyles": lifestyles,
        "height_min_cm": height_min_cm,
        "height_max_cm": height_max_cm,
        "height_needs_clarification": height_needs_clarification,
        "profession_keywords": profession_keywords,
    }


def _is_visible(profile: dict, field: str) -> bool:
    return profile.get("visibility", {}).get(field, False)


def _matches(profile: dict, constraints: dict) -> bool:
    if constraints["unknown_locations"]:
        return False
    if constraints["age_min"] is not None and profile["age"] < constraints["age_min"]:
        return False
    if constraints["age_max"] is not None and profile["age"] > constraints["age_max"]:
        return False
    if constraints["gender"] and profile["gender"] != constraints["gender"]:
        return False
    if constraints["cities"] and (
        not _is_visible(profile, "city") or profile["city"] not in constraints["cities"]
    ):
        return False
    if constraints["cultures"] and (
        not _is_visible(profile, "culture_community")
        or profile["culture_community"] not in constraints["cultures"]
    ):
        return False
    if constraints["regions"] and (
        not _is_visible(profile, "region") or profile["region"] not in constraints["regions"]
    ):
        return False
    if constraints["languages"] and not any(
        _is_visible(profile, "mother_tongue")
        and language == profile["mother_tongue"]
        for language in constraints["languages"]
    ):
        return False
    if constraints["interests"] and (
        not _is_visible(profile, "interests")
        or not any(interest in profile["interests"] for interest in constraints["interests"])
    ):
        return False
    if constraints["religions"] and (
        not _is_visible(profile, "religion") or profile["religion"] not in constraints["religions"]
    ):
        return False
    if constraints["countries"] and (
        not _is_visible(profile, "country") or profile["country"] not in constraints["countries"]
    ):
        return False
    if constraints["castes"] and (
        not _is_visible(profile, "caste") or profile["caste"] not in constraints["castes"]
    ):
        return False
    if constraints["gotras"] and (
        not _is_visible(profile, "gotra") or profile["gotra"] not in constraints["gotras"]
    ):
        return False
    if constraints["diets"] and (
        not _is_visible(profile, "diet") or profile["diet"] not in constraints["diets"]
    ):
        return False
    if constraints["smoking"] and (
        not _is_visible(profile, "smoking") or profile["smoking"] not in constraints["smoking"]
    ):
        return False
    if constraints["social_drinking"] and (
        not _is_visible(profile, "social_drinking")
        or profile["social_drinking"] not in constraints["social_drinking"]
    ):
        return False
    if constraints["lifestyles"] and (
        not _is_visible(profile, "lifestyle") or profile["lifestyle"] not in constraints["lifestyles"]
    ):
        return False
    if constraints["height_min_cm"] is not None or constraints["height_max_cm"] is not None:
        if not _is_visible(profile, "height_cm"):
            return False
        if constraints["height_min_cm"] is not None and profile["height_cm"] < constraints["height_min_cm"]:
            return False
        if constraints["height_max_cm"] is not None and profile["height_cm"] > constraints["height_max_cm"]:
            return False
    if constraints["profession_keywords"] and not _is_visible(profile, "profession"):
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
    for values in (
        "cities",
        "cultures",
        "regions",
        "languages",
        "interests",
        "religions",
        "countries",
        "castes",
        "gotras",
        "diets",
        "smoking",
        "social_drinking",
        "lifestyles",
    ):
        for value in constraints[values]:
            ignored.update(value.casefold().split())
    ignored.update({"tall", "short", "height", "cm", "centimeter", "centimeters", "social", "drinker"})
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


def _unsupported_query_terms(query: str) -> list[str]:
    known_values = (
        _CITIES
        + _CULTURES
        + _REGIONS
        + _LANGUAGES
        + _INTERESTS
        + _RELIGIONS
        + _COUNTRIES
        + _CASTES
        + _GOTRAS
        + _DIETS
        + _SMOKING_OPTIONS
        + _SOCIAL_DRINKING_OPTIONS
        + _LIFESTYLES
        + _MOTHER_TONGUES
    )
    known_words = set(_STOP_WORDS)
    known_words.update(
        {
            "under", "below", "younger", "older", "over", "above", "taller",
            "height", "tall", "short", "cm", "centimeter", "centimeters",
            "social", "drinker", "drinking", "smoker", "smoking",
            "non", "at", "least", "minimum", "min", "between", "and",
            "country", "state", "city", "diet", "caste", "gotra", "lifestyle",
            "active", "balanced", "home", "oriented", "hobby", "hobbies",
            "mother", "tongue",
        }
    )
    for value in known_values:
        known_words.update(_normalize_term(word) for word in re.findall(r"[a-zA-Z]+", value))
    for label, keywords in _PROFESSION_TERMS.items():
        known_words.add(_normalize_term(label))
        known_words.update(_normalize_term(keyword) for keyword in keywords)
    for gender_terms in _GENDER_TERMS.values():
        known_words.update(gender_terms)

    return sorted(
        {
            _normalize_term(term)
            for term in re.findall(r"[a-zA-Z]{3,}", query)
            if _normalize_term(term) not in known_words
        }
    )


def _relevance_score(profile: dict, query_terms: set[str]) -> int:
    searchable_values = [
        profile["gender"],
        str(profile["age"]),
    ]
    for field in (
        "profession",
        "culture_community",
        "city",
        "region",
        "religion",
        "mother_tongue",
        "caste",
        "gotra",
        "diet",
        "smoking",
        "social_drinking",
        "lifestyle",
    ):
        if _is_visible(profile, field) and profile.get(field):
            searchable_values.append(profile[field])
    if _is_visible(profile, "interests"):
        searchable_values.extend(profile["interests"])
    searchable_terms = {
        _normalize_term(term)
        for term in re.findall(
            r"[a-zA-Z]{3,}",
            " ".join(searchable_values),
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
    if constraints["height_needs_clarification"]:
        return "What minimum height in centimeters should I use?", []

    matching = [profile for profile in PROFILES if _matches(profile, constraints)]
    query_terms = _search_terms(query, constraints)
    unsupported_terms = set(_unsupported_query_terms(query))
    query_terms.difference_update(unsupported_terms)
    has_supported_criteria = any(
        (
            constraints["age_min"] is not None,
            constraints["age_max"] is not None,
            constraints["gender"],
            constraints["cities"],
            constraints["cultures"],
            constraints["regions"],
            constraints["languages"],
            constraints["interests"],
            constraints["religions"],
            constraints["countries"],
            constraints["castes"],
            constraints["gotras"],
            constraints["diets"],
            constraints["smoking"],
            constraints["social_drinking"],
            constraints["lifestyles"],
            constraints["height_min_cm"] is not None,
            constraints["height_max_cm"] is not None,
            constraints["profession_keywords"],
        )
    )
    if unsupported_terms and not has_supported_criteria:
        return _NO_MATCH_REPLY, []
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
        matching = [profile for profile in matching if _is_visible(profile, "interests")]
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

    unsupported_terms = _unsupported_query_terms(query)

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
            constraints["countries"],
            constraints["castes"],
            constraints["gotras"],
            constraints["diets"],
            constraints["smoking"],
            constraints["social_drinking"],
            constraints["lifestyles"],
            constraints["height_min_cm"],
            constraints["height_max_cm"],
        )
    ) or constraints["height_needs_clarification"]

    if constraints["height_needs_clarification"] and any(
        value is not None
        for value in (constraints["height_min_cm"], constraints["height_max_cm"])
    ):
        clarifying_question = "Please use a height between 100 and 250 centimeters."
    elif constraints["height_needs_clarification"]:
        clarifying_question = "What minimum height in centimeters should I use?"
    else:
        clarifying_question = "Happy to help. Which age range and city should I look in?"

    return {
        "looking_for": looking_for,
        "age_min": age_min,
        "age_max": age_max,
        "country": constraints["countries"][0] if constraints["countries"] else (
            "India" if city or region or religion or profession or gender else None
        ),
        "state": region,
        "city": city,
        "religion": religion,
        "mother_tongue": constraints["languages"][0] if constraints["languages"] else None,
        "profession": profession,
        "height_min_cm": constraints["height_min_cm"],
        "height_max_cm": constraints["height_max_cm"],
        "caste": constraints["castes"][0] if constraints["castes"] else None,
        "gotra": constraints["gotras"][0] if constraints["gotras"] else None,
        "diet": constraints["diets"][0] if constraints["diets"] else None,
        "smoking": constraints["smoking"],
        "social_drinking": constraints["social_drinking"],
        "lifestyle": constraints["lifestyles"][0] if constraints["lifestyles"] else None,
        "hobbies": constraints["interests"],
        "needs_clarification": needs_clarification,
        "clarifying_question": clarifying_question if needs_clarification else None,
        "unsupported_terms": unsupported_terms,
        "age_clamped": age_clamped,
    }


def card_payload(profile: dict) -> dict:
    first_name = profile["name"].split()[0]
    return {
        "profile_id": profile["id"],
        "first_name": first_name,
        "age": profile["age"],
        "city": profile["city"] if _is_visible(profile, "city") else None,
        "profession": (
            profile["profession"].split(" / ")[0]
            if _is_visible(profile, "profession")
            else None
        ),
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

    if re.search(r"\b(first message|message opener|conversation starter)\b", query, re.IGNORECASE):
        profile = next(
            (item for item in PROFILES if _is_visible(item, "interests")),
            None,
        )
        if profile is None:
            return {
                "reply": "I couldn't find a profile with visible interests to suggest a first message for.",
                "criteria": None,
                "total": 0,
                "cards": [],
                "has_more": False,
            }
        interest = profile["interests"][0]
        reply = (
            f"Here's a conversation starter for {profile['name'].split()[0]}, based on their "
            f"interest in {interest}: \"I noticed you enjoy {interest}. "
            "What first got you interested in it?\""
        )
        return {
            "reply": reply,
            "criteria": None,
            "total": 1,
            "cards": [card_payload(profile)],
            "has_more": False,
        }

    criteria = extract_criteria(query)
    if criteria["needs_clarification"]:
        clarification = criteria["clarifying_question"]
        if criteria["unsupported_terms"]:
            clarification = (
                "I can't search on that, but I can use supported profile details. "
                + clarification
            )
        return {
            "reply": clarification,
            "criteria": criteria,
            "total": 0,
            "cards": [],
            "has_more": False,
        }

    constraints = _query_constraints(query)
    constraints["age_min"] = criteria["age_min"]
    constraints["age_max"] = criteria["age_max"]
    matches = [
        profile
        for profile in PROFILES
        if _matches(profile, constraints)
    ]
    matches.sort(key=lambda profile: profile["id"])
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
        reply += (
            " I can't search on that, but I can use details like age, location, height, "
            "diet, religion, mother tongue, profession, and interests."
        )
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
    if criteria["height_min_cm"] is not None and criteria["height_max_cm"] is not None:
        parts.append(
            f"between {criteria['height_min_cm']} and {criteria['height_max_cm']} cm tall"
        )
    elif criteria["height_min_cm"] is not None:
        parts.append(f"at least {criteria['height_min_cm']} cm tall")
    elif criteria["height_max_cm"] is not None:
        parts.append(f"under {criteria['height_max_cm']} cm tall")
    if criteria["diet"]:
        parts.append(criteria["diet"])
    if criteria["caste"]:
        parts.append(f"from {criteria['caste']}")
    if criteria["gotra"]:
        parts.append(f"from gotra {criteria['gotra']}")
    if criteria["lifestyle"]:
        parts.append(f"with a {criteria['lifestyle']} lifestyle")
    if criteria["smoking"] == ["non-smoker"]:
        parts.append("who don't smoke")
    elif criteria["smoking"]:
        parts.append("who smoke occasionally or regularly")
    if criteria["social_drinking"]:
        parts.append("who drink socially")
    if criteria["hobbies"]:
        parts.append(f"who enjoy {', '.join(criteria['hobbies'])}")
    if not parts:
        return "Here's what I looked for."
    return "Here's what I looked for: " + ", ".join(parts) + "."
