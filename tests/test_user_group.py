from tests.base import BaseTestCase


class UserGroupTestCase(BaseTestCase):
    def base_get(self, api, json=None):
        return self.get(f"/user-group{api}", json)

    def base_post(self, api, json):
        return self.post(f"/user-group{api}", json)

    def api_purview(self):
        return self.base_get("/purview")

    def test_purview(self):
        response = self.api_purview()
        self.assertIn("ok", response["msg"])
