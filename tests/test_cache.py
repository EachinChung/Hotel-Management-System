from tests.base import BaseTestCase


class CacheTestCase(BaseTestCase):

    def add_test_user(self):
        """
        添加测试用户
        :return:
        """
        # 登录管理员用户，添加用户「测试删除缓存」
        token = self.login().json()["data"]["token"]["accessToken"]
        self.session.post(f"{self.url}/users", json={
            "phone": "13309999999",
            "name": "测试删除缓存",
            "user_group_id": 2
        }, headers={
            "Authorization": f"bearer {token}"
        })

        # 登录测试用户
        test_token = self.login("13309999999", "13309999999").json()["data"]["token"]
        return token, test_token["accessToken"], test_token["refreshToken"]

    def get_new_test_user_token(self, test_token, test_refresh_token):
        """
        重新获取测试用户的token
        :param test_token:
        :param test_refresh_token:
        :return:
        """
        # 测试被修改的用户要重新获取token
        re_register = self.session.get(f"{self.url}/users/groups/purview", headers={
            "Authorization": f"bearer {test_token}"
        }).json()

        # 测试被修改用户正常获取新的访问令牌
        new_token = self.session.patch(f"{self.url}/oauth/", headers={
            "Authorization": f"bearer {test_refresh_token}"
        }).json()

        return re_register, new_token

    def test_cache_after_token_expired(self):
        response = self.session.patch(f"{self.url}/oauth/", headers={
            "Authorization": f"bearer {self.phone}-6DDEB6569FFD1E6EAF42FDA1BF349205"
        }).json()
        self.assertEqual(401, response["err"])

    def test_cache_after_purview_update(self):
        # 登录缓存权限
        token = self.login().json()["data"]["token"]["accessToken"]
        self.assertIsNotNone(self.r.get(f"{self.phone}-purview"))

        # 删除缓存
        self.r.delete(f"{self.phone}-purview")
        self.assertIsNone(self.r.get(f"{self.phone}-purview"))

        # 检测是否自动更新缓存
        response = self.session.get(f"{self.url}/users", json=dict(page=1, per_page=1, query=""), headers={
            "Authorization": f"bearer {token}"
        }).json()

        self.assertIn("ok", response["msg"])
        self.assertIsNotNone(self.r.get(f"{self.phone}-purview"))

    def test_cache_after_update_user(self):
        token, test_token, test_refresh_token = self.add_test_user()

        # 账户权重为1
        response = self.session.get(f"{self.url}/users/groups/purview", headers={
            "Authorization": f"bearer {test_token}"
        }).json()
        self.assertEqual(1, response["data"]["weight"])

        # 用管理员用户修改刚添加的测试用户
        self.session.put(f"{self.url}/users/13309999999", json={
            "name": "测试删除缓存",
            "user_group_id": 3
        }, headers={
            "Authorization": f"bearer {token}"
        })

        re_register, new_token = self.get_new_test_user_token(test_token, test_refresh_token)
        self.assertEqual("请重新登录", re_register["msg"])
        self.assertEqual("ok", new_token["msg"])

        # 账户权重为2
        response = self.session.get(f"{self.url}/users/groups/purview", headers={
            "Authorization": f"bearer {new_token['data']['accessToken']}"
        }).json()
        self.assertEqual(2, response["data"]["weight"])

    def test_cache_after_del_user(self):
        token, test_token, test_refresh_token = self.add_test_user()

        # 用管理员用户删除刚添加的测试用户
        self.session.delete(f"{self.url}/users/13309999999", headers={
            "Authorization": f"bearer {token}"
        })

        re_register, new_token = self.get_new_test_user_token(test_token, test_refresh_token)
        self.assertEqual("请重新登录", re_register["msg"])
        self.assertEqual("该账号已被注销", new_token["msg"])
