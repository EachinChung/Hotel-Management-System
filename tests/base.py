import os
import unittest

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        self.url = os.environ.get('API_URL')

    def login(self, phone="13711164450", password="qwerty"):
        return self.session.post(
            url=f"{self.url}/oauth/login",
            json={
                "phone": phone,
                "password": password
            }
        )

    def post(self, uri, json):
        token = self.login().json()["data"]["token"]["accessToken"]
        return self.session.post(f"{self.url}{uri}", json=json, headers={
            "Authorization": f"bearer {token}"
        }).json()

    def get(self, uri, params=None):
        token = self.login().json()["data"]["token"]["accessToken"]
        return self.session.get(f"{self.url}{uri}", params=params, headers={
            "Authorization": f"bearer {token}"
        }).json()
