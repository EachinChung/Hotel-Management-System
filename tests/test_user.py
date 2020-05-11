from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):
    def base_get(self, api, json):
        return self.get(f"/user{api}", json)

    def base_post(self, api, json):
        return self.post(f"/user{api}", json)

    def api_add_user(self, json):
        return self.base_post("/add", json)

    def test_add_user(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 2
        })

        self.assertIn("测试用户", response["msg"])

    def test_add_user_err_repeat(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertIn("账号重复", response["msg"])

    def test_add_user_err_weight(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 1
        })
        self.assertIn("只能创建比自己权重低的账户", response["msg"])
