import http.client
import yaml

class Hero:

    def __init__(self):
        self.callsign = None
        self.faction = None
        self.token = None
        self.debug = False


    def __str__(self) -> str:
        return f"callsign: {self.callsign}\nfaction: {self.faction}\ntoken: {self.token}\ndebug: {self.debug}"

    def init_from_file(self, filename):
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


    def write_to_file(self, filename):
        data = {
                 "callsign": self.callsign,
                 "faction": self.faction,
                 "token": self.token
               }

        # Write YAML file
        with io.open(filename, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


    def _call_endpoint(self, method, authenticated, path, data):
        host = "https://api.spacetraders.io/v2"
        conn = http.client.HTTPSConnection(host)
        headers = {
                    "Host": host,
                    "Content-Type": "application/json"
                  }
        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"

        conn.request(method, path, headers=headers)
        response = conn.getresponse()
        if self.debug:
            print(response.status, response.reason)
        return response

    def _get_auth(self, path, data):
        return self._call_endpoint("GET", True, path, data)

    def _get_noauth(self, path, data):
        return self._call_endpoint("GET", False, path, data)

    def _post_auth(self, path, data):
        return self._call_endpoint("POST", True, path, data)

    def _post_noauth(self, path, data):
        return self._call_endpoint("POST", False, path, data)
