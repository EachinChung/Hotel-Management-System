from tests.base import BaseTestCase


class RoomTestCase(BaseTestCase):
    def base_room_get(self, api, json=None):
        return self.get(f"/room{api}", json)

    def base_room_post(self, api, json):
        return self.post(f"/room{api}", json)

    def api_room_add(self, json):
        return self.base_room_post("/add", json)

    def api_room_del(self, json):
        return self.base_room_post("/del", json)

    def api_room_update(self, json):
        return self.base_room_post("/update", json)

    def api_room_list(self, json):
        return self.base_room_post("/list", json)

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

    def test_room_update(self):
        response = self.api_room_update(dict(
            room_id=1002,
            room_type_id=1,
            floor=2,
            is_discounted=True
        ))
        self.assertIn("1002", response["msg"])

    def test_room_update_err_room(self):
        response = self.api_room_update(dict(
            room_id=9999,
            room_type_id=1,
            floor=2,
            is_discounted=True
        ))
        self.assertIn("该房间不存在", response["msg"])

    def test_room_del(self):
        response = self.api_room_del(dict(room_id=1001))
        self.assertIn('1001', response["msg"])

    def test_room_del_err_room(self):
        response = self.api_room_del(dict(room_id=1011))
        self.assertIn("该房间不存在", response["msg"])

    def test_room_list(self):
        response = self.api_room_list(dict(page=1, per_page=20))
        self.assertIn("ok", response["msg"])
