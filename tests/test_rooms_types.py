from hotel.extensions import db
from tests.base import BaseTestCase


class RoomTypeTestCase(BaseTestCase):

    def base_get(self, api, json=None):
        return self.get(f"/rooms/types{api}", json)

    def base_post(self, api, json):
        return self.post(f"/rooms/types{api}", json)

    def base_put(self, api, json):
        return self.put(f"/rooms/types{api}", json)

    def base_delete(self, api):
        return self.delete(f"/rooms/types{api}")

    def api_room_type_add(self, json):
        return self.base_post("", json)

    def api_room_type_del(self, room_type_id):
        return self.base_delete(f"/{room_type_id}")

    def api_room_type_update(self, room_type_id, json):
        return self.base_put(f"/{room_type_id}", json)

    def api_room_type_list(self):
        return self.base_get("/ids")

    def api_room_type(self):
        return self.base_get("")

    def api_get_price(self, room_type_id):
        return self.get(f"/rooms/types/{room_type_id}/prices")

    def api_add_price(self, room_type_id, json):
        return self.post(f"/rooms/types/{room_type_id}/prices", json)

    def api_put_price(self, room_type_id, price_id, json):
        return self.put(f"/rooms/types/{room_type_id}/prices/{price_id}", json)

    def api_del_price(self, room_type_id, price_id):
        return self.delete(f"/rooms/types/{room_type_id}/prices/{price_id}")

    def test_room_type(self):
        response = self.api_room_type()
        self.assertIn("ok", response["msg"])

    def test_room_type_list(self):
        response = self.api_room_type_list()
        self.assertIn("ok", response["msg"])

    def test_room_type_base(self):
        response = self.api_room_type_add(dict(
            room_type="豪华大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("豪华大床房", response["msg"])
        db.session.remove()

        room_type = self.api_room_type_list()
        response = self.api_room_type_update(room_type["data"]["items"][-1]["room_type_id"], dict(
            room_type="标准大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("房间类型重复", response["msg"])
        db.session.remove()

        response = self.api_room_type_update(room_type["data"]["items"][-1]["room_type_id"], dict(
            room_type="海景大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("海景大床房", response["msg"])
        db.session.remove()

        response = self.api_room_type_del(room_type["data"]["items"][-1]["room_type_id"])
        self.assertIn("海景大床房", response["msg"])

    def test_room_type_add_err_repeat(self):
        response = self.api_room_type_add(dict(
            room_type="标准大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("房间类型重复", response["msg"])

    def test_room_type_update_err_room_type(self):
        response = self.api_room_type_update(999999, dict(
            room_type="标准大床房",
            number_of_beds=1,
            number_of_people=2,
            price_tag=300
        ))
        self.assertIn("该房型不存在", response["msg"])

    def test_room_type_del_err_room_type(self):
        response = self.api_room_type_del(999999)
        self.assertIn("该房型不存在", response["msg"])

    def test_price(self):
        response = self.api_add_price(1, dict(customer_type="会员", price=12.1))
        self.assertEqual("会员 添加成功", response["msg"])

        price_id = self.api_get_price(1)
        self.assertEqual("ok", price_id["msg"])

        response = self.api_put_price(999099, price_id["data"]["items"][0]["id"], dict(customer_type="会员", price=12.1))
        self.assertEqual("提交信息不合法", response["msg"])
        response = self.api_put_price(999099, 999099, dict(customer_type="会员", price=12.1))
        self.assertEqual("该价格类型不存在", response["msg"])
        response = self.api_put_price(1, price_id["data"]["items"][0]["id"], dict(customer_type="会员", price=121.1))
        self.assertEqual("会员 修改成功", response["msg"])

        response = self.api_del_price(999099, price_id["data"]["items"][0]["id"])
        self.assertEqual("提交信息不合法", response["msg"])
        response = self.api_del_price(999099, 999099)
        self.assertEqual("该价格类型不存在", response["msg"])
        response = self.api_del_price(1, price_id["data"]["items"][0]["id"])
        self.assertEqual("会员 删除成功", response["msg"])
