import http.client
import yaml
import json

class Hero:
    """ Class representing the player """

    def __init__(self):
        self.callsign = None
        self.faction = None
        self.token = None
        self.debug = False

    def __str__(self) -> str:
        return f"callsign: {self.callsign}\nfaction: {self.faction}\ntoken: {self.token}\ndebug: {self.debug}"

    def init_from_file(self, filename:str):
        with open(filename, "r") as stream:
            try:
                obj = yaml.safe_load(stream)
                self.callsign = obj["callsign"]
                self.faction = obj["faction"]
                self.token = obj.get("token", None)
                self.debug = obj.get("debug", False)
                if self.debug:
                    print(self)
            except yaml.YAMLError as exc:
                print(exc)
                print(f"Unable to read from file named {filename}")

        # check for token
        if self.token is None:
            resp = self._register()
            if self.debug:
                print(resp)
            self.token = resp.get("data", {}).get("token", None)

            if self.token is not None:
                with open(filename, "w+") as stream:
                    try:
                        data = {
                                 "debug": self.debug,
                                 "callsign": self.callsign,
                                 "faction": self.faction,
                                 "token": self.token
                               }
                        stream.write(yaml.dump(data))
                    except yaml.YAMLError as exc:
                        print(exc)
                        print(f"Unable to write to file named {filename}")
            else:
                print("Unable to get token")

    def _register(self) -> dict:
        return self._post_noauth("register", {"symbol": self.callsign, "faction": self.faction})

    def _call_endpoint(self, method:str, authenticated:bool, path:str, data: dict) -> dict:
        host = "api.spacetraders.io"
        conn = http.client.HTTPSConnection(host)
        headers = { "Host": host, "Content-Type": "application/json" }

        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"

        if data is not None:
            conn.request(method, f"/v2/{path}", json.dumps(data), headers=headers)
        else:
            conn.request(method, f"/v2/{path}", headers=headers)

        response = conn.getresponse()
        if self.debug:
            print(response.status, response.reason)

        raw_data = response.read()
        encoding = response.info().get_content_charset('utf8')
        return json.loads(raw_data.decode(encoding))

    def _get_auth(self, path:str, data:dict) -> dict:
        return self._call_endpoint("GET", True, path, data)

    def _get_noauth(self, path:str, data:dict) -> dict:
        return self._call_endpoint("GET", False, path, data)

    def _post_auth(self, path:str, data:dict) -> dict:
        return self._call_endpoint("POST", True, path, data)

    def _post_noauth(self, path:str, data:dict) -> dict:
        return self._call_endpoint("POST", False, path, data)
