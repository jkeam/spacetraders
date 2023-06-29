import http.client
import yaml
import json
from datetime import datetime as dt

class Spacetrader:
    """ Represents the spacetracer API """
    def __init__(self, token:str, debug: bool) -> None:
        self.token = token
        self.debug = debug

    def get_auth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("GET", True, path, data)

    def get_noauth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("GET", False, path, data)

    def post_auth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("POST", True, path, data)

    def post_noauth(self, path:str, data:dict = {}) -> dict:
        return self._call_endpoint("POST", False, path, data)

    # Helper Methods

    def _call_endpoint(self, method:str, authenticated:bool, path:str, data: dict) -> dict:
        """ Actually hits the API endpoint """
        host = "api.spacetraders.io"
        conn = http.client.HTTPSConnection(host)
        headers = { "Host": host, "Content-Type": "application/json" }

        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"

        if data is not None and len(data) > 0:
            conn.request(method, f"/v2/{path}", json.dumps(data), headers=headers)
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
        return json.loads(raw_data.decode(encoding))

class ShipPoint:
    """ Point of a route """
    def __init__(self, point:dict) -> None:
        self.symbol:str = point["symbol"]
        self.type:str = point["type"]
        self.system:str = point["systemSymbol"]
        self.x:int = point["x"]
        self.y:int = point["y"]

    def __str__(self) -> str:
        return f"symbol: {self.symbol}, type: {self.type}, system: {self.system}, x: {self.x}, y: {self.y}"

class ShipRoute:
    """ Ship route """
    def __init__(self, route:dict) -> None:
        self.departure = ShipPoint(route["departure"])
        self.destination = ShipPoint(route["destination"])
        self.arrival_at = dt.fromisoformat(route["arrival"])
        self.departure_at = dt.fromisoformat(route["departureTime"])

    def __str__(self) -> str:
        return f"departure: {self.departure}, self.destination: {self.destination}, arrival_at: {self.arrival_at}, departure_at: {self.departure_at}"

class ShipNav:
    """ ShipNav """
    def __init__(self, ship_nav:dict) -> None:
        self.system:str = ship_nav["systemSymbol"]
        self.waypoint = Location(ship_nav["waypointSymbol"])
        self.route = ShipRoute(ship_nav["route"])
        self.status:str = ship_nav["status"]
        self.flight_mode:str = ship_nav["flightMode"]

    def __str__(self) -> str:
        return f"system: {self.system}, waypoint: {self.waypoint}, route: {self.route}, status: {self.route}, flight_mode: {self.flight_mode}"

class ShipCrew:
    """ Ship Crew """
    def __init__(self, crew:dict) -> None:
        self.current:int = crew["current"]
        self.capacity:int = crew["capacity"]
        self.required:int = crew["required"]
        self.rotation:str = crew["rotation"]
        self.morale:int = crew["morale"]
        self.wages:int = crew["wages"]

    def __str__(self) -> str:
        return f"current: {self.current}, capacity: {self.capacity}, required: {self.required}, rotation: {self.rotation}, morale: {self.morale}, wages: {self.wages}"

class ShipCargo:
    """ Ship Cargo """
    def __init__(self, cargo:dict) -> None:
        self.capacity:int = cargo["capacity"]
        self.units:int = cargo["units"]
        self.inventory:list = cargo["inventory"]

    def __str__(self) -> str:
        return f"capacity: {self.capacity}, units: {self.units}, inventory: {self.inventory}"

class ShipFuel:
    """ Ship fuel """
    def __init__(self, fuel: dict) -> None:
        self.current:int = fuel["current"]
        self.capacity:int = fuel["capacity"]
        self.consumed:int = fuel["consumed"]["amount"]
        self.consumed_at = dt.fromisoformat(fuel["consumed"]["timestamp"])

    def __str__(self) -> str:
        return f"current: {self.current}, capacity: {self.capacity}, consumed: {self.consumed}, consumed_at: {self.consumed_at}"

class Ship:
    """ Ship """
    def __init__(self, ship:dict) -> None:
        self.symbol:str = ship["symbol"]
        self.nav = ShipNav(ship["nav"])
        self.crew = ShipCrew(ship["crew"])
        self.cargo = ShipCargo(ship["cargo"])
        self.fuel = ShipFuel(ship["fuel"])
        # missing frame, reactor, engine, modules, mounts, registration

    def __str__(self) -> str:
        return f"symbol: {self.symbol}, nav: {self.nav}, crew: {self.crew}, cargo: {self.cargo}, fuel: {self.fuel}"

class ContractDelivery:
    """ The thing to deliver as described in the terms """
    def __init__(self, cont:dict) -> None:
        self.trade:str = cont["tradeSymbol"]
        self.destination = cont["destinationSymbol"]
        self.units_required = cont["unitsRequired"]
        self.units_fulfilled = cont["unitsFulfilled"]

    def __str__(self) -> str:
        return f"trade: {self.trade}, destination: {self.destination}, units_required: {self.units_required}, units_fulfilled: {self.units_fulfilled}"

class ContractTerm:
    """ Represents the terms of the contract """
    def __init__(self, cont:dict) -> None:
        self.deadline = dt.fromisoformat(cont["deadline"])
        self.payment_on_accepted:int = cont["payment"]["onAccepted"]
        self.payment_on_fulfilled:int= cont["payment"]["onFulfilled"]
        self.deliveries = list(map(lambda d: ContractDelivery(d), cont.get("deliver", [])))

    def __str__(self) -> str:
        return f"deadline: {self.deadline}, payment_on_accepted: {self.payment_on_accepted}, payment_on_fulfilled: {self.payment_on_fulfilled}, deliveries: {list(map(lambda d: d.__str__(), self.deliveries))}"

class Contract:
    """ Represents a contract """
    def __init__(self, cont:dict) -> None:
        self.id:str = cont["id"]
        self.faction:str = cont["factionSymbol"]
        self.type:str = cont["type"]
        self.terms = ContractTerm(cont["terms"])
        self.accepted:bool = cont["accepted"]
        self.fulfilled:bool = cont["fulfilled"]
        self.expiration = dt.fromisoformat(cont["expiration"])
        self.deadline = dt.fromisoformat(cont["deadlineToAccept"])

    def __str__(self) -> str:
        return f"id: {self.id}, faction: {self.faction}, type: {self.type}, terms: {self.terms}, accepted: {self.accepted}, fulfilled: {self.fulfilled}, expiration: {self.expiration}, deadline: {self.deadline}"

class Location:
    """ Represents a location """
    def __init__(self, coordinate:str) -> None:
        data = coordinate.split("-")
        self.sector = data[0]
        self.system = f"{data[0]}-{data[1]}"
        self.waypoint = coordinate

    def __str__(self) -> str:
        return f"sector: {self.sector}, system: {self.system}, waypoint: {self.waypoint}"

class WaypointTrait():
    """ Waypoint Trait, a characteristic of a waypoint """
    def __init__(self, loc:dict) -> None:
        self.symbol:str = loc["symbol"]
        self.name:str = loc["name"]
        self.description:str = loc["description"]

    def __str__(self) -> str:
        return f"symbol: {self.symbol}, name: {self.name}, description: {self.description}"

class Waypoint(Location):
    """ Waypoint, like a location but with way more data """
    def __init__(self, loc:dict) -> None:
        super().__init__(loc["symbol"])
        self.type:str = loc["type"]
        self.x:int = loc["x"]
        self.y:int = loc["y"]
        self.orbitals = list(map(lambda o: Location(o["symbol"]), loc["orbitals"]))
        self.traits = list(map(lambda t: WaypointTrait(t), loc["traits"]))

    def __str__(self) -> str:
        return f"location: {super().__str__()}, type: {self.type}, x: {self.x}, y: {self.y}, orbitals: {list(map(lambda o: o.__str__(), self.orbitals))}"

class Hero:
    """ Class representing the player """
    def __init__(self):
        self.callsign:str
        self.faction:str
        self.token:str
        self.debug = False
        self.contracts:list[Contract]
        self.headquarter_waypoints:list[Waypoint]
        self.headquarter:Location
        self.headquarter_shipyard:Waypoint
        self.account_id:str
        self.credits:int
        self.api:Spacetrader
        self.ships:list[Ship]

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
                self.api = Spacetrader(self.token, self.debug)
                if self.debug:
                    print(self)
            except yaml.YAMLError as exc:
                print(exc)
                print(f"Unable to read from file named {filename}")

        # check for token
        if self.token is None or self.token == "":
            resp = self.api.post_noauth("register", {"symbol": self.callsign, "faction": self.faction})
            if self.debug:
                print(resp)
            self.token = resp.get("data", {}).get("token", None)
            self.api.token = self.token

            # save token
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

    def get_agent(self) -> dict:
        """ Get agent info """
        info = self.api.get_auth("my/agent")["data"]
        if self.debug:
            print(info)

        self.headquarter = Location(info["headquarters"])
        self.account_id = info["accountId"]
        self.credits = info["credits"]
        if self.debug:
            print("Get Agent")
            print(self.headquarter)
        return info

    def get_my_ships(self) -> dict:
        """ Get my ships """
        info = self.api.get_auth("my/ships")["data"]
        self.ships = list(map(lambda s: Ship(s), info))
        if self.debug:
            print("Get my ships")
            for s in self.ships:
                print(s)
        return info

    def get_contracts(self) -> list[Contract]:
        """ Get contracts """
        info = self.api.get_auth("my/contracts")["data"]
        self.contracts = list(map(lambda c: Contract(c), info))
        if self.debug:
            print("Get Contracts")
            for c in self.contracts:
                print(c)
        return self.contracts

    def accept_all_contracts(self) -> None:
        """ Accept all contracts """
        self.get_contracts()
        for c in self.contracts:
            self.accept_contract(c)
        self.get_contracts()

    def accept_contract(self, contract:Contract) -> dict:
        """ Accept a particular contract """
        info = self.api.post_auth(f"my/contracts/{contract.id}/accept")
        if self.debug:
            print("Accept Contract")
            print(info)
        return info

    def get_headquarter_waypoints(self) -> list[Waypoint]:
        """ Get the HQ Waypoints """
        raw_waypoints = self.api.get_auth(f"systems/{self.headquarter.system}/waypoints")["data"]
        self.headquarter_waypoints = list(map(lambda w: Waypoint(w), raw_waypoints))
        if self.debug:
            print("Get Waypoints")
            for w in self.headquarter_waypoints:
                print(w)
        return self.headquarter_waypoints

    def get_headquarter_ships(self) -> dict:
        """ Get all the ships from headquarter """
        if len(self.headquarter_waypoints) == 0:
            self.get_headquarter_waypoints()

        shipyard:Waypoint|None = None
        for w in self.headquarter_waypoints:
            if shipyard is None:
                for t in w.traits:
                    if t.symbol == "SHIPYARD":
                        shipyard = w

        if shipyard is not None:
            self.headquarter_shipyard = shipyard
            if self.debug:
                print("Found Shipyard")
                print(shipyard)
            raw_ships = self.api.get_auth(f"systems/{self.headquarter.system}/waypoints/{shipyard.waypoint}/shipyard")["data"]
            if self.debug:
                print("Get Headquarter Ships")
                print(raw_ships)
            return raw_ships
        return {}

    def get_headquarter_mining_drones(self) -> list[dict]:
        """ Get headquarter mining drones """
        ships = list(filter(lambda s: s["type"] == "SHIP_MINING_DRONE", self.get_headquarter_ships()["ships"]))
        if self.debug:
            print("Get Headquarter mining drones")
            print(ships)
        return ships

    def buy_headquarter_mining_drone(self) -> dict:
        """ Buy mining drone at the HQ """
        self.get_headquarter_mining_drones()
        raw_purchase = self.api.post_auth(f"my/ships", {"shipType": "SHIP_MINING_DRONE", "waypointSymbol": self.headquarter_shipyard.waypoint})["data"]
        if self.debug:
            print("Buy Headquarter Mining Drone")
            print(raw_purchase)
        return raw_purchase
