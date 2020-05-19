from hotel.extensions import db
from tests.base import BaseTestCase


class UserGroupTestCase(BaseTestCase):

    def base_get(self, api, json=None):
        return self.get(f"/users/groups{api}", json)

    def base_post(self, api, json):
        return self.post(f"/users/groups{api}", json)

    def base_put(self, api, json):
        return self.put(f"/users/groups{api}", json)

    def base_delete(self, api):
        return self.delete(f"/users/groups{api}")

    def api_purview(self):
        return self.base_get("/purview")

    def api_group_id_list(self):
        return self.base_get("/ids")

    def api_add_user_group(self, json):
        return self.base_post("/", json)

    def api_update_user_group(self, user_group_id, json):
        return self.base_put(f"/{user_group_id}", json)

    def api_del_user_group(self, user_group_id):
        return self.base_delete(f"/{user_group_id}")

    def api_user_group_list(self, json):
        return self.base_get("/", json)

    def get_user_group_list(self):
        return self.api_user_group_list(dict(page=1, per_page=100, query=""))

    def test_purview(self):
        response = self.api_purview()
        self.assertEqual("ok", response["msg"])

    def test_group_id_list(self):
        response = self.api_group_id_list()
        self.assertEqual("ok", response["msg"])

    def test_user_group_base(self):
        response = self.api_add_user_group({
            "group_name": "测试用户组",
            "description": "",
            "weight": 100
        })
        self.assertEqual("测试用户组 添加成功", response["msg"])

        user_group_list = self.get_user_group_list()
        response = self.api_update_user_group(user_group_list["data"]["items"][-1]["id"], {
            "group_name": "测试呀",
            "description": "",
            "weight": 100
        })

        self.assertEqual("测试呀 修改成功", response["msg"])
        response = self.api_del_user_group(user_group_list["data"]["items"][-1]["id"])
        self.assertEqual("测试呀 删除成功", response["msg"])

    def test_user_group_err_not_purview(self):
        self.post("/users/", {
            "phone": "11111119999",
            "name": "测试用户",
            "user_group_id": 4
        })
        db.session.remove()
        test_token = self.login("11111119999", "11111119999").get_json()["data"]["token"]["accessToken"]

        response = self.client.post("/users/groups/", json={
            "group_name": "测试用户组",
            "description": "",
            "weight": 100
        }, headers={
            "Authorization": f"bearer {test_token}"
        }).get_json()

        self.assertEqual("该用户非超级管理员", response["msg"])
        self.delete("/users/11111119999")

    def test_add_user_group_err_repeat(self):
        response = self.api_add_user_group({
            "group_name": "无权限用户组",
            "description": "",
            "weight": 10
        })
        self.assertEqual("用户组重复", response["msg"])

    def test_add_user_group_err_weight(self):
        response = self.api_add_user_group({
            "group_name": "测试用户组",
            "description": "",
            "weight": -10
        })
        self.assertEqual("不能创建权重小于 1 的账户组", response["msg"])
        response = self.api_add_user_group({
            "group_name": "测试用户组",
            "description": "",
            "weight": 0
        })
        self.assertEqual("不能创建权重小于 1 的账户组", response["msg"])

    def test_add_user_group_err_fail_user_not_body(self):
        response = self.api_add_user_group({})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_add_user_group(None)
        self.assertEqual('缺少参数', response['msg'])

    def test_update_user_group_err_sudo(self):
        response = self.api_update_user_group(1, {
            "group_name": "修改管理员",
            "description": "",
            "weight": 100
        })
        self.assertEqual("不能修改超级管理员", response["msg"])

    def test_update_user_group_err_not_user_group(self):
        response = self.api_update_user_group(1000000, {
            "group_name": "未知用户组",
            "description": "",
            "weight": 100
        })
        self.assertEqual("该用户组不存在", response["msg"])

    def test_update_user_group_err_not_body(self):
        response = self.api_update_user_group(1000000, {})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_update_user_group(1000000, None)
        self.assertEqual('缺少参数', response['msg'])

    def test_del_user_group_err_not_user_group(self):
        response = self.api_del_user_group(1000000)
        self.assertEqual("该用户组不存在", response["msg"])

    def test_del_user_group_err_weight(self):
        response = self.api_del_user_group(1)
        self.assertEqual("不能删除超级管理员", response["msg"])

    def test_user_group_list(self):
        response = self.get_user_group_list()
        self.assertEqual("ok", response["msg"])
