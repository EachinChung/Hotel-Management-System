from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):
    def base_get(self, api, json):
        return self.get(f"/user{api}", json)

    def base_post(self, api, json):
        return self.post(f"/user{api}", json)

    def api_add_user(self, json):
        return self.base_post("/add", json)

    def api_del_user(self, json):
        return self.base_post("/del", json)

    def test_add_user(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 2
        })

        self.assertIn("测试用户", response["msg"])

    def test_fail_add_user_illegal_phone(self):
        response = self.api_add_user({
            "phone": "15811119dfg",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertIn('提交信息不合法', response['msg'])

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

    def test_fail_add_user_not_body(self):
        response = self.api_add_user({})
        self.assertIn('缺少参数', response['msg'])
        response = self.api_add_user(None)
        self.assertIn('缺少参数', response['msg'])

    def test_del_user(self):
        response = self.api_del_user(dict(phone="15811119999"))
        self.assertIn("测试用户", response["msg"])

    def test_fail_del_user_illegal_phone(self):
        response = self.api_del_user(dict(phone="15811111YES"))
        self.assertIn('提交信息不合法', response['msg'])

    def test_del_user_err_oneself(self):
        response = self.api_del_user(dict(phone=self.phone))
        self.assertIn("不能删除当前账户", response["msg"])

    def test_del_user_err_weight(self):
        response = self.api_del_user(dict(phone="15811111111"))
        self.assertIn("只能删除比自己权重低的账户", response["msg"])

    def test_fail_del_user_not_body(self):
        response = self.api_del_user({})
        self.assertIn('缺少参数', response['msg'])
        response = self.api_del_user(None)
        self.assertIn('缺少参数', response['msg'])
