from tests.base import BaseTestCase


class UserGroupTestCase(BaseTestCase):
    def base_get(self, api, json=None):
        return self.get(f"/user-group{api}", json)

    def base_post(self, api, json):
        return self.post(f"/user-group{api}", json)

    def api_purview(self):
        return self.base_get("/purview")

    def api_group_id_list(self):
        return self.base_get("/id-list")

    def test_purview(self):
        response = self.api_purview()
        self.assertIn("ok", response["msg"])

    def test_group_id_list(self):
        response = self.api_group_id_list()
        self.assertIn("ok", response["msg"])
