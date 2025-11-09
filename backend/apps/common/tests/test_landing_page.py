from rest_framework import status
from rest_framework.test import APITestCase


class LandingContentAPITests(APITestCase):

    def setUp(self) -> None:
        self.url = "/api/content/landing/"

    def test_get_landing_content_success(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("hero", data)
        self.assertIn("for_whom", data)
        self.assertIn("why_worth", data)
        self.assertIn("footer_links", data)

    def test_landing_content_structure(self) -> None:
        response = self.client.get(self.url)
        data = response.json()

        self.assertIsInstance(data["hero"], dict)
        self.assertIn("title", data["hero"])
        self.assertIn("cta_text", data["hero"])

        self.assertIsInstance(data["for_whom"], list)
        if data["for_whom"]:
            self.assertIn("title", data["for_whom"][0])
            self.assertIn("desc", data["for_whom"][0])

        self.assertIsInstance(data["why_worth"], list)
        if data["why_worth"]:
            self.assertIn("title", data["why_worth"][0])

        self.assertIsInstance(data["footer_links"], dict)
        self.assertIn("left", data["footer_links"])
        self.assertIn("right", data["footer_links"])
        self.assertIsInstance(data["footer_links"]["left"], list)
