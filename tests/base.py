from unittest import TestCase
from urllib.parse import urlencode
from warnings import simplefilter

from dotenv import find_dotenv, load_dotenv

from hotel import create_app

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

    def tearDown(self):
        self.app_context.pop()

    def login(self, phone=None, password=None):
        if phone is None: phone = self.phone
        if password is None: password = self.password
        return self.client.post(
            "/oauth/",
            json={
                "phone": phone,
                "password": password
            }
        )

    def get(self, uri, params=None):
        if params is not None: uri += f"?{urlencode(params)}"
        token = self.login().get_json()["data"]["token"]["accessToken"]
        return self.client.get(uri, headers={
            "Authorization": f"bearer {token}"
        }).get_json()

    def post(self, uri, json):
        token = self.login().get_json()["data"]["token"]["accessToken"]
        return self.client.post(uri, json=json, headers={
            "Authorization": f"bearer {token}"
        }).get_json()

    def put(self, uri, json):
        token = self.login().get_json()["data"]["token"]["accessToken"]
        return self.client.put(uri, json=json, headers={
            "Authorization": f"bearer {token}"
        }).get_json()

    def patch(self, uri, json):
        token = self.login().get_json()["data"]["token"]["accessToken"]
        return self.client.patch(uri, json=json, headers={
            "Authorization": f"bearer {token}"
        }).get_json()

    def delete(self, uri, *, json=None):
        token = self.login().get_json()["data"]["token"]["accessToken"]
        return self.client.delete(uri, json=json, headers={
            "Authorization": f"bearer {token}"
        }).get_json()
