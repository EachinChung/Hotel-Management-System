from tests.base import BaseTestCase


class CacheTestCase(BaseTestCase):
    def test_purview(self):
        """
        测试权限的缓存
        :return:
        """
        # 登录缓存权限
        token = self.login().json()["data"]["token"]["accessToken"]
        self.assertIsNotNone(self.r.get(f"{self.phone}-purview"))

        # 删除缓存
        self.r.delete(f"{self.phone}-purview")
        self.assertIsNone(self.r.get(f"{self.phone}-purview"))

        # 检测是否自动更新缓存
        response = self.session.post(f"{self.url}/user/list", json=dict(page=1, per_page=1, query=""), headers={
            "Authorization": f"bearer {token}"
        }).json()

        self.assertIn("ok", response["msg"])
        self.assertIsNotNone(self.r.get(f"{self.phone}-purview"))
