import logging

import requests
import urllib3
import os

urllib3.disable_warnings()

METABASE_API_SSL_VERIFY = True if os.environ.get('METABASE_API_SSL_VERIFY') in ["1", "true"] else False


class NotFoundError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class Metabase:
    def __init__(self, host: str, user: str, password: str, token: str = None, debug: bool = False,
                 logger: logging.Logger = None):
        self._host = host
        self.user = user
        self.password = password
        self._token = token
        self.debug = debug
        self.logger = logger

    @property
    def host(self):
        host = self._host

        if not host.startswith("http"):
            host = "https://" + self._host

        return host.rstrip("/")

    @host.setter
    def host(self, value):
        self._host = value

    def log_request(self, address, payload=None, info: str = None):
        if self.debug and self.logger:
            msg = "METABASE_REQUEST :: " + address
            if payload:
                msg += " :: " + str(payload)
            if info:
                msg += " :: " + info
            self.logger.debug(msg)

    @property
    def token(self):
        if self._token is None:
            address = self.host + "/api/session"
            payload = {"username": self.user, "password": self.password}
            self.log_request(address, payload)
            response = requests.post(
                address,
                verify=METABASE_API_SSL_VERIFY,
                json=payload
            )

            if response.status_code != 200:
                raise AuthenticationError(response.content.decode())

            self._token = response.json()["id"]

        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def headers(self):
        return {"X-Metabase-Session": self.token}

    def get(self, endpoint: str, **kwargs):
        address = self.host + endpoint
        return requests.get(address, headers=self.headers, verify=METABASE_API_SSL_VERIFY, **kwargs)

    def post(self, endpoint: str, **kwargs):
        address = self.host + endpoint
        return requests.post(address, headers=self.headers, verify=METABASE_API_SSL_VERIFY, **kwargs)

    def put(self, endpoint: str, **kwargs):
        address = self.host + endpoint
        return requests.put(address, headers=self.headers, verify=METABASE_API_SSL_VERIFY, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return requests.delete(self.host + endpoint, headers=self.headers, verify=METABASE_API_SSL_VERIFY, **kwargs)
