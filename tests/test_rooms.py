from tests.base import BaseTestCase


class RoomTestCase(BaseTestCase):
    def base_get(self, api, json=None):
        return self.get(f"/rooms{api}", json)

    def base_post(self, api, json):
        return self.post(f"/rooms{api}", json)

    def base_put(self, api, json):
        return self.put(f"/rooms{api}", json)

    def base_delete(self, api):
        return self.delete(f"/rooms{api}")

    def api_room_add(self, json):
        return self.base_post("/", json)

    def api_room_del(self, room_id):
        return self.base_delete(f"/{room_id}")

    def api_room_update(self, room_id, json):
        return self.base_put(f"/{room_id}", json)

    def api_room_list(self, json):
        return self.base_get("/", json)

    def test_room_add(self):
        response = self.api_room_add(dict(
            room_id=1001,
            room_type_id=1,
            floor=1
        ))
        self.assertIn("1001", response["msg"])

    def test_room_add_err_repeat(self):
        response = self.api_room_add(dict(
            room_id=1001,
            room_type_id=1,
            floor=1
        ))
        self.assertIn("房间重复", response["msg"])

    def test_room_add_err_not_body(self):
        response = self.api_room_add({})
        self.assertEqual('缺少参数', response['msg'])
        response = self.api_room_add(None)
        self.assertEqual('缺少参数', response['msg'])

    def test_room_update(self):
        response = self.api_room_update(1002, dict(
            room_type_id=1,
            floor=2,
            is_discounted=True
        ))
        self.assertIn("1002", response["msg"])

    def test_room_update_err_room(self):
        response = self.api_room_update(9999, dict(
            room_type_id=1,
            floor=2,
            is_discounted=True
        ))
        self.assertIn("该房间不存在", response["msg"])

    def test_room_del(self):
        response = self.api_room_del(1001)
        self.assertIn('1001', response["msg"])

    def test_room_del_err_room(self):
        response = self.api_room_del(1011)
        self.assertIn("该房间不存在", response["msg"])

    def test_room_list(self):
        response = self.api_room_list(dict(page=1, per_page=20))
        self.assertIn("ok", response["msg"])
