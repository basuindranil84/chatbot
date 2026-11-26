import json
import unittest

from app.services.profile_service import (
    DATA_PATH,
    PROFILES,
    _matches,
    _query_constraints,
    card_payload,
    extract_criteria,
    search_profiles,
    search_profiles_page,
)
from scripts.generate_profiles import build_profiles


class ProfileDatasetTests(unittest.TestCase):
    def test_dataset_has_500_synthetic_profiles_in_requested_age_range(self):
        dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        self.assertTrue(dataset["synthetic"])
        self.assertEqual(500, len(PROFILES))
        self.assertEqual({ "Female", "Male" }, {profile["gender"] for profile in PROFILES})
        self.assertTrue(all(21 <= profile["age"] <= 45 for profile in PROFILES))
        self.assertEqual(500, len({profile["id"] for profile in PROFILES}))
        self.assertEqual(500, len({profile["name"] for profile in PROFILES}))
        required_fields = {
            "name", "gender", "age", "city", "region", "culture_community",
            "languages", "religion", "profession", "education", "interests",
            "short_bio", "relationship_preferences", "country", "mother_tongue",
            "height_cm", "caste", "gotra", "diet", "smoking",
            "social_drinking", "lifestyle", "visibility",
        }
        self.assertTrue(all(required_fields <= profile.keys() for profile in PROFILES))
        self.assertTrue(
            all(
                isinstance(profile["visibility"].get(field), bool)
                for profile in PROFILES
                for field in (
                    "religion",
                    "mother_tongue",
                    "height_cm",
                    "caste",
                    "gotra",
                    "diet",
                    "smoking",
                    "social_drinking",
                    "lifestyle",
                )
            )
        )
        self.assertEqual(PROFILES, build_profiles())

    def test_search_filters_by_profession_city_and_age(self):
        reply, results = search_profiles("Find doctors in Kolkata aged 28 to 32")

        self.assertIn("1 matching profile", reply)
        self.assertEqual(1, len(results))
        profile = results[0]
        self.assertEqual("Kolkata", profile["city"])
        self.assertEqual("Doctor / Physician", profile["profession"])
        self.assertTrue(28 <= profile["age"] <= 32)

    def test_search_filters_by_gender_and_location(self):
        _, results = search_profiles("female engineers in Bengaluru between 25 and 45")

        self.assertTrue(results)
        self.assertTrue(
            all(
                profile["gender"] == "Female"
                and profile["city"] == "Bengaluru"
                and "Engineer" in profile["profession"]
                and 25 <= profile["age"] <= 45
                for profile in results
            )
        )

    def test_results_are_limited_to_five(self):
        _, results = search_profiles("Find profiles")

        self.assertEqual(5, len(results))

    def test_unmatched_criteria_return_standard_message_without_profiles(self):
        expected = (
            "I couldn't find profiles matching those details. "
            "Try changing the location, age range, or profession."
        )
        for query in (
            "Find male doctors in Atlantis aged 28 to 32",
            "Find profiles who enjoy kayaking",
        ):
            with self.subTest(query=query):
                reply, results = search_profiles(query)
                self.assertEqual(expected, reply)
                self.assertEqual([], results)

    def test_search_filters_by_spoken_language(self):
        _, results = search_profiles("Find profiles speaking Tamil")

        self.assertTrue(results)
        self.assertTrue(all("Tamil" in profile["languages"] for profile in results))

    def test_first_message_suggestion_uses_profile_interests(self):
        reply, results = search_profiles("Help me write a first message")

        self.assertEqual(1, len(results))
        self.assertIn(results[0]["name"], reply)
        self.assertIn(results[0]["interests"][0], reply)

    def test_favorites_are_not_fabricated(self):
        reply, results = search_profiles("Show my favorites")

        self.assertEqual([], results)
        self.assertIn("aren't available", reply)

    def test_vague_request_needs_clarification(self):
        page = search_profiles_page("someone nice")

        self.assertTrue(page["criteria"]["needs_clarification"])
        self.assertEqual([], page["cards"])
        self.assertIn("Which age range and city", page["reply"])
        self.assertIn("can't search on that", page["reply"])

    def test_age_below_eighteen_is_clamped(self):
        criteria = extract_criteria("women aged 15 to 25")

        self.assertEqual(18, criteria["age_min"])
        self.assertEqual(25, criteria["age_max"])
        self.assertTrue(criteria["age_clamped"])

    def test_unsupported_term_does_not_suppress_supported_matches(self):
        baseline = search_profiles_page("Find doctors in Kolkata aged 28 to 32")
        with_unsupported_term = search_profiles_page(
            "Find doctors in Kolkata aged 28 to 32 with high income"
        )

        self.assertEqual(
            [card["profile_id"] for card in baseline["cards"]],
            [card["profile_id"] for card in with_unsupported_term["cards"]],
        )
        self.assertIn("income", with_unsupported_term["criteria"]["unsupported_terms"])
        self.assertIn("can't search on", with_unsupported_term["reply"])

    def test_vague_tall_request_asks_for_minimum_height(self):
        page = search_profiles_page("Find doctors in Kolkata who are tall")

        self.assertTrue(page["criteria"]["needs_clarification"])
        self.assertEqual([], page["cards"])
        self.assertIn("minimum height", page["reply"])

    def test_numeric_height_filter_uses_only_visible_profile_values(self):
        page = search_profiles_page("Find doctors in Kolkata at least 175 cm")

        self.assertTrue(page["cards"])
        found = {profile["id"]: profile for profile in PROFILES}
        self.assertTrue(
            all(
                found[card["profile_id"]]["height_cm"] >= 175
                and found[card["profile_id"]]["visibility"]["height_cm"]
                for card in page["cards"]
            )
        )

    def test_show_more_excludes_profiles_from_the_previous_page(self):
        first_page = search_profiles_page("Find profiles aged 21 to 45")
        seen_ids = [card["profile_id"] for card in first_page["cards"]]
        second_page = search_profiles_page("Find profiles aged 21 to 45", seen_ids)
        next_ids = [card["profile_id"] for card in second_page["cards"]]

        self.assertEqual(5, len(seen_ids))
        self.assertEqual(5, len(next_ids))
        self.assertFalse(set(seen_ids) & set(next_ids))

    def test_added_searchable_attributes_require_owner_visibility(self):
        vegetarian_page = search_profiles_page("Find vegetarian profiles")
        found = {profile["id"]: profile for profile in PROFILES}
        self.assertTrue(vegetarian_page["cards"])
        self.assertTrue(
            all(
                found[card["profile_id"]]["diet"] == "vegetarian"
                and found[card["profile_id"]]["visibility"]["diet"]
                for card in vegetarian_page["cards"]
            )
        )

        hidden_religion_profile = next(
            profile
            for profile in PROFILES
            if not profile["visibility"]["religion"]
        )
        religion_constraints = _query_constraints(
            f"Find profiles of religion {hidden_religion_profile['religion']}"
        )
        self.assertFalse(_matches(hidden_religion_profile, religion_constraints))
        self.assertNotIn("religion", card_payload(hidden_religion_profile))

        hidden_city_profile = next(
            profile
            for profile in PROFILES
            if not profile["visibility"]["city"]
        )
        city_constraints = _query_constraints(
            f"Find profiles in {hidden_city_profile['city']}"
        )
        self.assertFalse(_matches(hidden_city_profile, city_constraints))
        self.assertIsNone(card_payload(hidden_city_profile)["city"])

    def test_caste_gotra_smoking_drinking_lifestyle_and_hobbies_are_searchable(self):
        searches = (
            ("caste", PROFILES[0]["caste"], f"Find profiles from {PROFILES[0]['caste']}"),
            ("gotra", PROFILES[0]["gotra"], f"Find profiles from {PROFILES[0]['gotra']}"),
            ("smoking", "non-smoker", "Find non-smokers"),
            ("social_drinking", ["occasional", "regular"], "Find social drinkers"),
            ("lifestyle", "active", "Find profiles with an active lifestyle"),
            ("interests", "yoga", "Find profiles who enjoy yoga"),
            ("mother_tongue", "Bengali", "Find profiles with Bengali mother tongue"),
        )
        for field, expected, query in searches:
            with self.subTest(field=field):
                page = search_profiles_page(query)
                self.assertTrue(page["cards"])
                results = {profile["id"]: profile for profile in PROFILES}
                if field == "interests":
                    self.assertTrue(
                        all(
                            expected in results[card["profile_id"]][field]
                            and results[card["profile_id"]]["visibility"][field]
                            for card in page["cards"]
                        )
                    )
                else:
                    self.assertTrue(
                        all(
                            (
                                results[card["profile_id"]][field] in expected
                                if isinstance(expected, list)
                                else results[card["profile_id"]][field] == expected
                            )
                            and results[card["profile_id"]]["visibility"][field]
                            for card in page["cards"]
                        )
                    )

    def test_unknown_location_does_not_broaden_a_supported_search(self):
        page = search_profiles_page("Find doctors in Atlantis")

        self.assertEqual([], page["cards"])
        self.assertIn("couldn't find", page["reply"])

    def test_unsupported_only_request_asks_for_supported_criteria(self):
        page = search_profiles_page("Find profiles with high income")

        self.assertTrue(page["criteria"]["needs_clarification"])
        self.assertEqual([], page["cards"])
        self.assertIn("Which age range and city", page["reply"])
        self.assertIn("can't search on that", page["reply"])

    def test_search_page_preserves_visible_interest_first_message_flow(self):
        page = search_profiles_page("Help me write a first message")

        self.assertEqual(1, len(page["cards"]))
        self.assertIn("conversation starter", page["reply"])

    def test_card_payload_excludes_private_profile_text_and_keeps_a_view_link(self):
        page = search_profiles_page("Find doctors in Kolkata aged 28 to 32")

        self.assertTrue(page["cards"])
        card = page["cards"][0]
        self.assertIsNone(card["photo_url"])
        self.assertTrue(card["profile_url"].startswith("/profile/"))
        self.assertNotIn("short_bio", card)


if __name__ == "__main__":
    unittest.main()
