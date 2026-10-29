import re

from django.test import SimpleTestCase, override_settings

from .store import store

CODE_PATTERN = re.compile(r"^[A-Za-z0-9]{6}$")


@override_settings(MINILIEN_ADMIN_TOKEN="jeton-de-test")
class LinkApiTest(SimpleTestCase):
    def setUp(self):
        store.clear()

    def create_link(self, url):
        response = self.client.post("/api/liens", {"url": url}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        return response.json()["code"]

    def test_creates_a_short_link_for_a_valid_url(self):
        response = self.client.post("/api/liens", {"url": "https://openclassrooms.com/fr/"},
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertRegex(body["code"], CODE_PATTERN)
        self.assertEqual(response["Location"], f"/api/liens/{body['code']}")
        self.assertEqual(body["url"], "https://openclassrooms.com/fr/")
        self.assertEqual(body["lienCourt"], f"http://localhost:8080/r/{body['code']}")
        self.assertEqual(body["visites"], 0)

    def test_rejects_an_invalid_url(self):
        response = self.client.post("/api/liens", {"url": "ftp://exemple.fr"}, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "URL_INVALIDE")

    def test_redirects_and_counts_visits(self):
        code = self.create_link(url="https://exemple.fr/page")

        response = self.client.get(f"/r/{code}")
        self.client.get(f"/r/{code}")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://exemple.fr/page")
        self.assertEqual(self.client.get(f"/api/liens/{code}").json()["visites"], 2)

    def test_lists_links(self):
        self.create_link(url="https://exemple.fr/1")
        self.create_link(url="https://exemple.fr/2")

        response = self.client.get("/api/liens")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_returns_404_for_an_unknown_code(self):
        response = self.client.get("/r/XXXXXX")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], "LIEN_INTROUVABLE")

    def test_rejects_deletion_without_a_valid_token(self):
        code = self.create_link(url="https://exemple.fr")

        self.assertEqual(self.client.delete(f"/api/liens/{code}").status_code, 401)
        self.assertEqual(self.client.delete(f"/api/liens/{code}", headers={"X-Admin-Token": "mauvais"}).status_code, 401)

    def test_deletes_a_link_with_the_right_token(self):
        code = self.create_link(url="https://exemple.fr")

        response = self.client.delete(f"/api/liens/{code}", headers={"X-Admin-Token": "jeton-de-test"})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/api/liens/{code}").status_code, 404)