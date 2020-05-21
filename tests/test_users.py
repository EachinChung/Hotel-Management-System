from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):

    def base_get(self, api, json=None):
        return self.get(f"/users{api}", json)

    def base_post(self, api, json):
        return self.post(f"/users{api}", json)

    def base_patch(self, api, json):
        return self.patch(f"/users{api}", json)

    def base_put(self, api, json):
        return self.put(f"/users{api}", json)

    def base_delete(self, api):
        return self.delete(f"/users{api}")

    def api_add_user(self, json):
        return self.base_post("", json)

    def api_update_user(self, phone, json):
        return self.base_put(f"/{phone}", json)

    def api_del_user(self, phone):
        return self.base_delete(f"/{phone}")

    def api_user_list(self, json):
        return self.base_get(f"", json)

    def api_set_activation(self, phone, json):
        return self.base_patch(f"/{phone}", json)

    def test_user_base(self):
        # 新建一个用户
        self.api_del_user(15811119999)
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertEqual("测试用户 添加成功", response["msg"])

        # 获取用户列表
        response = self.api_user_list(dict(page=1, per_page=1, query=""))
        self.assertEqual("ok", response["msg"])

        # 修改用户
        response = self.api_update_user(15811119999, {
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("测试员 修改成功", response["msg"])

        # 尝试登录新建用户
        test_token = self.login("15811119999", "15811119999")
        self.assertIn("accessToken", test_token.get_data(as_text=True))

        # 冻结新建用户
        response = self.api_set_activation(15811119999, {
            "is_activation": False
        })
        self.assertEqual("测试员 修改为非激活状态", response["msg"])

        response = self.client.get("/rooms/types/ids", headers={
            "Authorization": f'bearer {test_token.get_json()["data"]["token"]["accessToken"]}'
        }).get_json()
        self.assertEqual(401, response["err"])

        response = self.client.patch("/oauth", headers={
            "Authorization": f'bearer {test_token.get_json()["data"]["token"]["refreshToken"]}'
        }).get_json()
        self.assertEqual("该账号暂为冻结状态，请联系管理员", response["msg"])

        response = self.login("15811119999", "15811119999").get_json()
        self.assertEqual("该账号暂为冻结状态，请联系管理员", response["msg"])

        # 解封新建用户
        response = self.api_set_activation(15811119999, {
            "is_activation": True
        })
        self.assertEqual("测试员 修改为激活状态", response["msg"])

        test_token = self.login("15811119999", "15811119999")
        self.assertIn("accessToken", test_token.get_data(as_text=True))

        # 删除新建用户
        response = self.api_del_user(15811119999)
        self.assertEqual("测试员 删除成功", response["msg"])

    def test_set_activation_err(self):
        response = self.api_set_activation(999, {
            "is_activation": True
        })
        self.assertEqual("该用户不存在", response["msg"])

    def test_set_activation_illegal_weight(self):
        response = self.api_set_activation(self.phone, {
            "is_activation": True
        })
        self.assertEqual("只能修改比自己权重低的账户状态", response["msg"])

    def test_add_user_err_illegal_phone(self):
        response = self.api_add_user({
            "phone": "15811119dfg",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertEqual('提交信息不合法', response['msg'])

    def test_add_user_err_repeat(self):
        response = self.api_add_user({
            "phone": "13311119999",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertEqual("账号重复", response["msg"])

    def test_add_user_err_weight(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 1
        })
        self.assertEqual("只能创建比自己权重低的账户", response["msg"])

    def test_add_user_err_user_group(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 9999999
        })
        self.assertEqual("该用户组不存在", response["msg"])

    def test_add_user_err_fail_user_not_body(self):
        response = self.api_add_user({})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_add_user(None)
        self.assertEqual('缺少参数', response['msg'])

    def test_update_user_err_not_user(self):
        response = self.api_update_user(18999999990, {
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("该用户不存在", response["msg"])

    def test_update_user_err_not_weight(self):
        response = self.api_update_user(self.phone, {
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("只能修改比自己权重低的账户", response["msg"])

    def test_update_user_err_weight(self):
        response = self.api_update_user(13311119999, {
            "name": "测试员",
            "user_group_id": 1
        })
        self.assertEqual("只能修改为比自己权重低的账户", response["msg"])

    def test_update_user_err_not_user_group(self):
        response = self.api_update_user(13311119999, {
            "name": "测试员",
            "user_group_id": 99
        })
        self.assertEqual("该用户组不存在", response["msg"])

    def test_update_user_err_not_body(self):
        response = self.api_update_user(self.phone, {})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_update_user(self.phone, None)
        self.assertEqual('缺少参数', response['msg'])

    def test_del_user_err_illegal_phone(self):
        response = self.api_del_user("15811111YES")
        self.assertEqual('找不到此资源', response['msg'])

    def test_del_user_err_not_user(self):
        response = self.api_del_user(12345678910)
        self.assertEqual("该账号不存在", response["msg"])

    def test_del_user_err_oneself(self):
        response = self.api_del_user(self.phone)
        self.assertEqual("不能删除当前账户", response["msg"])

    def test_del_user_err_weight(self):
        response = self.api_del_user(15811111111)
        self.assertEqual("只能删除比自己权重低的账户", response["msg"])
