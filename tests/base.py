import unittest
from os import environ

from dotenv import find_dotenv, load_dotenv
from redis import StrictRedis
from requests import session

load_dotenv(find_dotenv())


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.session = session()
        self.phone = "13711164450"
        self.password = "qwerty"
        self.url = environ.get('API_URL')
        self.r = StrictRedis(host='localhost', port=6379, password=environ.get('REDIS_PASSWORD'), decode_responses=True)

    def login(self, phone=None, password=None):

        if phone is None:
            phone = self.phone
        if password is None:
            password = self.password

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
