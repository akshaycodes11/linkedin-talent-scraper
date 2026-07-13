import unittest

from parser import parse_profiles


class ParseProfilesLocationTests(unittest.TestCase):
    def test_uses_selected_location_when_exact_match_is_present(self):
        result = [{
            "title": "John Doe - Senior AI Engineer",
            "description": "Based in Bengaluru, India",
            "url": "https://www.linkedin.com/in/johndoe"
        }]

        parsed = parse_profiles(result, "AI Engineer", selected_location="Bengaluru")

        self.assertEqual(parsed[0]["location"], "Bengaluru")

    def test_falls_back_to_india_when_no_exact_match_is_found(self):
        result = [{
            "title": "John Doe - Senior AI Engineer",
            "description": "Based in Hyderabad, India",
            "url": "https://www.linkedin.com/in/johndoe"
        }]

        parsed = parse_profiles(result, "AI Engineer", selected_location="Bengaluru")

        self.assertEqual(parsed[0]["location"], "India")


if __name__ == "__main__":
    unittest.main()
