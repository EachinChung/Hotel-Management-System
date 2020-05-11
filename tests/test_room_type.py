from tests.base import BaseTestCase


class RoomTypeTestCase(BaseTestCase):
    def base_get(self, api, json=None):
        return self.get(f"/room-type{api}", json)

    def base_post(self, api, json):
        return self.post(f"/room-type{api}", json)

    def api_room_type_add(self, json):
        return self.base_post("/add", json)

    def api_room_type_del(self, json):
        return self.base_post("/del", json)

    def api_room_type_update(self, json):
        return self.base_post("/update", json)

    def api_room_type_list(self):
        return self.base_get("/list")

    def test_room_type_list(self):
        response = self.api_room_type_list()
        self.assertIn("ok", response["msg"])

    def test_room_type_add(self):
        response = self.api_room_type_add(dict(
            room_type="豪华大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("豪华大床房", response["msg"])

    def test_room_type_add_err_repeat(self):
        response = self.api_room_type_add(dict(
            room_type="豪华大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("房间类型重复", response["msg"])

    def test_room_type_update(self):
        room_type = self.api_room_type_list()
        response = self.api_room_type_update(dict(
            room_type_id=room_type["data"]["items"][1]["room_type_id"],
            room_type="海景大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("海景大床房", response["msg"])

    def test_room_type_update_err(self):
        room_type = self.api_room_type_list()
        response = self.api_room_type_update(dict(
            room_type_id=room_type["data"]["items"][1]["room_type_id"],
            room_type="标准大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("房间类型重复", response["msg"])

    def test_room_type_update_err_room_type(self):
        response = self.api_room_type_update(dict(
            room_type_id=999999,
            room_type="标准大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("该房型不存在", response["msg"])

    def test_room_type_del(self):
        room_type = self.api_room_type_list()
        response = self.api_room_type_del(dict(room_type_id=room_type["data"]["items"][1]["room_type_id"]))
        self.assertIn(room_type["data"]["items"][1]["room_type"], response["msg"])

    def test_room_type_del_err_room_type(self):
        response = self.api_room_type_del(dict(room_type_id=99999))
        self.assertIn("该房型不存在", response["msg"])
