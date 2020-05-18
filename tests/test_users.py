from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):

    def base_get(self, api, json=None):
        return self.get(f"/users{api}", json)

    def base_post(self, api, json):
        return self.post(f"/users{api}", json)

    def base_put(self, api, json):
        return self.put(f"/users{api}", json)

    def base_delete(self, api):
        return self.delete(f"/users{api}")

    def api_add_user(self, json):
        return self.base_post("/", json)

    def api_update_user(self, phone, json):
        return self.base_put(f"/{phone}", json)

    def api_del_user(self, phone):
        return self.base_delete(f"/{phone}")

    def api_user_list(self, json):
        return self.base_get(f"/", json)

    def test_user_base(self):
        response = self.api_add_user({
            "phone": "15811119999",
            "name": "测试用户",
            "user_group_id": 2
        })
        self.assertEqual("测试用户 添加成功", response["msg"])

        response = self.api_user_list(dict(page=1, per_page=1, query=""))
        self.assertEqual("ok", response["msg"])

        response = self.api_update_user(15811119999, {
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("测试员 修改成功", response["msg"])

        response = self.api_del_user(15811119999)
        self.assertEqual("测试员 删除成功", response["msg"])

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

    def test_add_user_err_fail_user_not_body(self):
        response = self.api_add_user({})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_add_user(None)
        self.assertEqual('缺少参数', response['msg'])

    def test_update_user_err_not_user(self):
        response = self.api_update_user(18999999990,{
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("该用户不存在", response["msg"])

    def test_update_user_err_not_weight(self):
        response = self.api_update_user(self.phone,{
            "name": "测试员",
            "user_group_id": 2
        })
        self.assertEqual("只能修改比自己权重低的账户", response["msg"])

    def test_update_user_err_weight(self):
        response = self.api_update_user(13311119999,{
            "name": "测试员",
            "user_group_id": 1
        })
        self.assertEqual("只能修改为比自己权重低的账户", response["msg"])

    def test_update_user_err_not_user_group(self):
        response = self.api_update_user(13311119999,{
            "name": "测试员",
            "user_group_id": 99
        })
        self.assertEqual("该用户组不存在", response["msg"])

    def test_update_user_err_not_body(self):
        response = self.api_update_user(self.phone,{})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_update_user(self.phone,None)
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
