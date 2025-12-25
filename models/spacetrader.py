import http.client
from json import dumps, loads

class Spacetrader:
    """ Represents the spacetracer API """
    def __init__(self, token:str, account_token:str, debug:bool=False) -> None:
        self.token = token
        self.account_token = account_token
        self.debug = debug

    def get_auth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("GET", True, path, data)

    def get_noauth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("GET", False, path, data)

    def post_auth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("POST", True, path, data)

    def post_noauth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("POST", True, path, data)

    # Helper Methods

    def _call_endpoint(self, method:str, authenticated:bool, path:str, data:dict) -> dict:
        """ Actually hits the API endpoint """
        host = "api.spacetraders.io"
        conn = http.client.HTTPSConnection(host)
        headers = { "Host": host }

        if authenticated:
            if self.token is not None and self.token != "":
                headers["Authorization"] = f"Bearer {self.token}"
            else:
                headers["Authorization"] = f"Bearer {self.account_token}"
        if data:
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"

        if data is not None and len(data) > 0:
            conn.request(method, f"/v2/{path}", dumps(data), headers=headers)
        else:
            conn.request(method, f"/v2/{path}", headers=headers)

        response = conn.getresponse()
        if self.debug:
            print(response.status, response.reason)

        raw_data = response.read()
        encoding = response.info().get_content_charset('utf8')
        # error debugging
        if self.debug and response.status != 200:
            print(raw_data)
        return loads(raw_data.decode(encoding))


