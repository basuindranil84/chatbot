import json
import unittest

from app.services.profile_service import DATA_PATH, PROFILES, search_profiles


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
            "short_bio", "relationship_preferences",
        }
        self.assertTrue(all(required_fields <= profile.keys() for profile in PROFILES))

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


if __name__ == "__main__":
    unittest.main()
