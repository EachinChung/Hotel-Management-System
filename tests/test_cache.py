from hotel.extensions import db
from hotel.my_redis import Redis
from tests.base import BaseTestCase


class CacheTestCase(BaseTestCase):

    def add_test_user(self):
        """
        添加测试用户
        :return:
        """
        # 登录管理员用户，添加用户「测试删除缓存」
        token = self.login().get_json()["data"]["token"]["accessToken"]
        self.client.post("/users", json={
            "phone": "13309999999",
            "name": "测试删除缓存",
            "user_group_id": 2
        }, headers={
            "Authorization": f"bearer {token}"
        })
        db.session.remove()
        # 登录测试用户
        test_token = self.login("13309999999", "13309999999").get_json()["data"]["token"]
        return token, test_token["accessToken"], test_token["refreshToken"]

    def get_new_test_user_token(self, test_token, test_refresh_token):
        """
        重新获取测试用户的token
        :param test_token:
        :param test_refresh_token:
        :return:
        """
        # 测试被修改的用户要重新获取token
        re_register = self.client.get("/users/purview", headers={
            "Authorization": f"bearer {test_token}"
        }).get_json()

        # 测试被修改用户正常获取新的访问令牌
        new_token = self.client.patch("/oauth", headers={
            "Authorization": f"bearer {test_refresh_token}"
        }).get_json()

        return re_register, new_token

    def test_cache_after_token_expired(self):
        response = self.client.patch("/oauth", headers={
            "Authorization": f"bearer {self.phone}-6DDEB6569FFD1E6EAF42FDA1BF349205"
        }).get_json()
        self.assertEqual(401, response["err"])

    def test_cache_after_purview_update(self):
        # 登录缓存权限
        token = self.login().get_json()["data"]["token"]["accessToken"]
        self.client.get("/users", json=dict(page=1, per_page=1, query=""), headers={
            "Authorization": f"bearer {token}"
        }).get_json()
        self.assertIsNotNone(Redis.get(f"{self.phone}-purview"))

        # 删除缓存
        Redis.delete(f"{self.phone}-purview")
        self.assertIsNone(Redis.get(f"{self.phone}-purview"))

        # 检测是否自动更新缓存
        response = self.client.get("/users", json=dict(page=1, per_page=1, query=""), headers={
            "Authorization": f"bearer {token}"
        }).get_json()

        self.assertIn("ok", response["msg"])
        self.assertIsNotNone(Redis.get(f"{self.phone}-purview"))

    def test_cache_after_update_user(self):
        token, test_token, test_refresh_token = self.add_test_user()

        # 账户权重为1
        response = self.client.get("/users/purview", headers={
            "Authorization": f"bearer {test_token}"
        }).get_json()
        self.assertEqual(1, response["data"]["weight"])

        # 用管理员用户修改刚添加的测试用户
        self.client.put(f"/users/13309999999", json={
            "name": "测试删除缓存",
            "user_group_id": 3
        }, headers={
            "Authorization": f"bearer {token}"
        })

        re_register, new_token = self.get_new_test_user_token(test_token, test_refresh_token)
        self.assertEqual("请重新登录", re_register["msg"])
        self.assertEqual("ok", new_token["msg"])

        # 账户权重为2
        response = self.client.get("/users/purview", headers={
            "Authorization": f"bearer {new_token['data']['accessToken']}"
        }).get_json()
        self.assertEqual(2, response["data"]["weight"])

    def test_cache_after_del_user(self):
        token, test_token, test_refresh_token = self.add_test_user()

        # 用管理员用户删除刚添加的测试用户
        self.client.delete("/users/13309999999", headers={
            "Authorization": f"bearer {token}"
        })

        re_register, new_token = self.get_new_test_user_token(test_token, test_refresh_token)
        self.assertEqual("请重新登录", re_register["msg"])
        self.assertEqual("该账号已被注销", new_token["msg"])
