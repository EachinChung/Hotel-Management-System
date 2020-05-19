from tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def api_refresh_token(self, token):
        return self.client.patch("/oauth/", headers={
            "Authorization": f"bearer {token}"
        })

    def test_login_user(self):
        response = self.login()
        self.assertIn("accessToken", response.get_data(as_text=True))

    def test_fail_login_err_phone(self):
        response = self.login(phone='11111111111', password='wrong-password')
        self.assertEqual('该账号不存在', response.get_json()['msg'])

    def test_fail_login_illegal_phone(self):
        response = self.login(phone='wrong-username', password='wrong-password')
        self.assertEqual('提交信息不合法', response.get_json()['msg'])

    def test_fail_login_err_password(self):
        response = self.login(password='wrong-password')
        self.assertEqual('密码错误', response.get_json()['msg'])

    def test_fail_login_null(self):
        response = self.login(phone='', password='')
        self.assertEqual('提交信息不合法', response.get_json()['msg'])

    def test_fail_login_null_password(self):
        response = self.login(password='')
        self.assertEqual('密码错误', response.get_json()['msg'])

    def test_fail_login_not_body(self):
        response = self.client.post("/oauth/")
        self.assertEqual('缺少参数', response.get_json()['msg'])
        response = self.client.post("/oauth/", json={})
        self.assertEqual('缺少参数', response.get_json()['msg'])

    def test_refresh_token(self):
        token = self.login().get_json()["data"]["token"]["refreshToken"]
        response = self.api_refresh_token(token)
        self.assertIn("accessToken", response.get_data(as_text=True))

    def test_refresh_not_token(self):
        response = self.client.patch(f"/oauth/")
        self.assertEqual("请重新登录", response.get_json()["msg"])

    def test_refresh_token_expired(self):
        token = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU4ODEwMTQ4MywiZXhwIjoxNTg4MTAxNDkzfQ.eyJwaG9uZSI6IjEzNzExMTExMTExIn0.fPPahOQi70q9rjXeJrjV5-PTSHP0pgtBCuRcPzh_R58LNJfJ3yAtZe0Sk6eHI5EnRTQ842FLv5a1-KU1yoLpIA"
        response = self.api_refresh_token(token)
        self.assertEqual("请重新登录", response.get_json()["msg"])

    def test_refresh_token_bad_sign(self):
        token = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU4ODEwMTM0OCwiZXhwIjoxNTkwNjkzMzQ4fQ.eyJwaG9uZSI6IjEzNzExMTEyMjIyIn0.UbmiYPn_RTfzj0uX0lAb_sjpDKcGkigCat2_Db1-w3Hr19lZT8QEV5ljv77KdpLf7VCLJbHvDiYurQFIy5NkwQ"
        response = self.api_refresh_token(token)
        self.assertEqual("请重新登录", response.get_json()["msg"])
