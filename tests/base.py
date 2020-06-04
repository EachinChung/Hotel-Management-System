from unittest import TestCase
from urllib.parse import urlencode
from warnings import simplefilter

from dotenv import find_dotenv, load_dotenv

from hotel import create_app
from hotel.my_redis import Redis

load_dotenv(find_dotenv())


class BaseTestCase(TestCase):
    def setUp(self):
        simplefilter('ignore', DeprecationWarning)
        app = create_app()
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()

        self.phone = "13711164450"
        self.password = "qwerty"

        Redis.hmset("test", {
            "name": "钟予乾",
            "phone": "13711164450",
            "weight": 0,
            "user_group": "超级管理员"
        })

    def tearDown(self):
        Redis.delete("test")
        self.app_context.pop()

    def login(self, phone=None, password=None):
        if phone is None: phone = self.phone
        if password is None: password = self.password
        return self.client.post(
            "/oauth",
            json={
                "phone": phone,
                "password": password
            }
        )

    def get(self, uri, params=None):
        if params is not None: uri += f"?{urlencode(params)}"
        return self.client.get(uri, headers={
            "Authorization": f"bearer test"
        }).get_json()

    def post(self, uri, json):
        return self.client.post(uri, json=json, headers={
            "Authorization": f"bearer test"
        }).get_json()

    def put(self, uri, json):
        return self.client.put(uri, json=json, headers={
            "Authorization": f"bearer test"
        }).get_json()

    def patch(self, uri, json):
        return self.client.patch(uri, json=json, headers={
            "Authorization": f"bearer test"
        }).get_json()

    def delete(self, uri, *, json=None):
        return self.client.delete(uri, json=json, headers={
            "Authorization": f"bearer test"
        }).get_json()
