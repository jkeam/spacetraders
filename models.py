import http.client
import yaml
import json
from datetime import datetime as dt
from time import sleep
from dataclasses import dataclass

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

@dataclass
class ShipPoint:
    """ Point of a route """
    symbol:str
    type:str
    system:str
    x:int
    y:int

@dataclass
class ShipRoute:
    """ Ship route """
    departure:ShipPoint
    destination:ShipPoint
    arrival_at:dt
    departure_at:dt

class ShipNav:
    """ ShipNav """
    def __init__(self, ship_nav:dict) -> None:
        self.system:str = ship_nav["systemSymbol"]
        self.waypoint = Location(ship_nav["waypointSymbol"])

        route = ship_nav["route"]
        departure = ShipPoint(
                route["departure"]["symbol"],
                route["departure"]["type"],
                route["departure"]["systemSymbol"],
                route["departure"]["x"],
                route["departure"]["y"])
        destination = ShipPoint(
                route["destination"]["symbol"],
                route["destination"]["type"],
                route["destination"]["systemSymbol"],
                route["destination"]["x"],
                route["destination"]["y"])
        arrival_at = dt.fromisoformat(route["arrival"])
        departure_at = dt.fromisoformat(route["departureTime"])
        self.route = ShipRoute(departure, destination, arrival_at, departure_at)

        self.status:str = ship_nav["status"]
        self.flight_mode:str = ship_nav["flightMode"]

    def __str__(self) -> str:
        return f"system: {self.system}, waypoint: {self.waypoint}, route: {self.route}, status: {self.status}, flight_mode: {self.flight_mode}"

@dataclass
class ShipCrew:
    """ Ship Crew """
    current:int
    capacity:int
    required:int
    rotation:str
    morale:int
    wages:int

@dataclass
class ShipCargoItem:
    """ Ship Cargo Item """
    symbol:str
    name:str
    description:str
    units:int

class ShipCargo:
    """ Ship Cargo """
    def __init__(self, cargo:dict) -> None:
        self.capacity:int = cargo["capacity"]
        self.units:int = cargo["units"]
        self.inventory:list[ShipCargoItem] = list(map(lambda i: ShipCargoItem(i["symbol"], i["name"], i["description"], i["units"]), cargo["inventory"]))

    def __str__(self) -> str:
        return f"ShipCargo(capacity: {self.capacity}, units: {self.units}, inventory: {list(map(lambda i: i.__str__(), self.inventory))})"

    def is_full(self) -> bool:
        """ Indicates if cargo is full """
        return self.capacity == self.units

@dataclass
class ShipFuel:
    """ Ship fuel """
    current:int
    capacity:int
    consumed:int
    consumed_at:dt

@dataclass
class ShipFrame:
    symbol:str
    name:str
    description:str
    module_slots:int
    mounting_points:int
    fuel_capacity:int
    condition:int
    power_requirement:int
    crew_requirement:int

class Ship:
    """ Ship """
    def __init__(self, api:Spacetrader, ship:dict) -> None:
        self.api = api
        self.name:str = ship["registration"]["name"]
        self.faction:str = ship["registration"]["factionSymbol"]
        self.role:str = ship["registration"]["role"]
        self.symbol:str = ship["symbol"]
        self.nav = ShipNav(ship["nav"])
        self.crew = ShipCrew(
                ship["crew"]["current"],
                ship["crew"]["capacity"],
                ship["crew"]["required"],
                ship["crew"]["rotation"],
                ship["crew"]["morale"],
                ship["crew"]["wages"])
        self.cargo = ShipCargo(ship["cargo"])

        self.fuel = ShipFuel(
                ship["fuel"]["current"],
                ship["fuel"]["capacity"],
                ship["fuel"]["consumed"]["amount"],
                ship["fuel"]["consumed"]["timestamp"])

        self.frame = ShipFrame(
                ship["frame"]["symbol"],
                ship["frame"]["name"],
                ship["frame"]["description"],
                ship["frame"]["moduleSlots"],
                ship["frame"]["mountingPoints"],
                ship["frame"]["fuelCapacity"],
                ship["frame"]["condition"],
                ship["frame"]["requirements"]["power"],
                ship["frame"]["requirements"]["crew"])

        # missing reactor, engine, modules, mounts

    def __str__(self) -> str:
        return f"Ship(name: {self.name}, faction: {self.faction}, role: {self.role}, symbol: {self.symbol}, nav: {self.nav}, crew: {self.crew}, cargo: {self.cargo}, fuel: {self.fuel}, frame: {self.frame})"

    def cargo_is_full(self) -> bool:
        """ Indicates if cargo is full """
        return self.cargo.is_full()

    def orbit(self) -> dict:
        """ Bring ship into orbit """
        return self.api.post_auth(f"my/ships/{self.symbol}/orbit")["data"]

    def fly(self, destination_waypoint_symbol:str) -> dict:
        """ Fly ship """
        return self.api.post_auth(f"my/ships/{self.symbol}/navigate", {"waypointSymbol": destination_waypoint_symbol})["data"]

    def dock(self) -> dict:
        """ Dock ship """
        return self.api.post_auth(f"my/ships/{self.symbol}/dock")

    def refuel(self) -> dict:
        """ Refuel ship """
        return self.api.post_auth(f"my/ships/{self.symbol}/refuel")

    def mine(self) -> dict:
        """ Mine resources """
        return self.api.post_auth(f"my/ships/{self.symbol}/extract")

    def get_cargo(self) -> dict:
        """ Get Cargo """
        return self.api.get_auth(f"my/ships/{self.symbol}/cargo")

    def view_market(self) -> dict:
        """ View Market, only works if we are at an asteroid field """
        return self.api.get_auth(f"systems/{self.nav.system}/waypoints/{self.nav.waypoint.waypoint}/market")

    def sell_all_cargo(self, except_symbols:list[str]) -> None:
        """ Sell all cargo """
        for c in self.cargo.inventory:
            if c.symbol not in except_symbols:
                self.api.post_auth(f"my/ships/{self.symbol}/sell", {"symbol": c.symbol, "units": c.units})

@dataclass
class ContractDelivery:
    """ The thing to deliver as described in the terms """
    trade:str
    destination:str
    units_required:int
    units_fulfilled:int

class ContractTerm:
    """ Represents the terms of the contract """
    def __init__(self, cont:dict) -> None:
        self.deadline = dt.fromisoformat(cont["deadline"])
        self.payment_on_accepted:int = cont["payment"]["onAccepted"]
        self.payment_on_fulfilled:int= cont["payment"]["onFulfilled"]
        self.deliveries = list(map(lambda d: ContractDelivery(d["tradeSymbol"], d["destinationSymbol"], d["unitsRequired"], d["unitsFulfilled"]), cont.get("deliver", [])))

    def __str__(self) -> str:
        return f"ContractTerm(deadline: {self.deadline}, payment_on_accepted: {self.payment_on_accepted}, payment_on_fulfilled: {self.payment_on_fulfilled}, deliveries: {list(map(lambda d: d.__str__(), self.deliveries))})"

class Contract:
    """ Represents a contract """
    def __init__(self, cont:dict) -> None:
        self.id:str = cont["id"]
        self.faction:str = cont["factionSymbol"]
        self.type:str = cont["type"]
        self.terms:ContractTerm = ContractTerm(cont["terms"])
        self.accepted:bool = cont["accepted"]
        self.fulfilled:bool = cont["fulfilled"]
        self.expiration:dt = dt.fromisoformat(cont["expiration"])
        self.deadline:dt = dt.fromisoformat(cont["deadlineToAccept"])

    def __str__(self) -> str:
        return f"Contract(id: {self.id}, faction: {self.faction}, type: {self.type}, terms: {self.terms}, accepted: {self.accepted}, fulfilled: {self.fulfilled}, expiration: {self.expiration}, deadline: {self.deadline})"

class Location:
    """ Represents a location """
    def __init__(self, coordinate:str) -> None:
        data = coordinate.split("-")
        self.sector:str = data[0]
        self.system:str = f"{data[0]}-{data[1]}"
        self.waypoint:str = coordinate

    def __str__(self) -> str:
        return f"Location(sector: {self.sector}, system: {self.system}, waypoint: {self.waypoint})"

@dataclass
class WaypointTrait():
    """ Waypoint Trait, a characteristic of a waypoint """
    symbol:str
    name:str
    description:str

class Waypoint(Location):
    """ Waypoint, like a location but with way more data """
    def __init__(self, loc:dict) -> None:
        super().__init__(loc["symbol"])
        self.type:str = loc["type"]
        self.x:int = loc["x"]
        self.y:int = loc["y"]
        self.orbitals:list[Location] = list(map(lambda o: Location(o["symbol"]), loc["orbitals"]))
        self.traits:list[WaypointTrait] = list(map(lambda t: WaypointTrait(t["symbol"], t["name"], t["description"]), loc["traits"]))

    def __str__(self) -> str:
        return f"Waypoint(location: {super().__str__()}, type: {self.type}, x: {self.x}, y: {self.y}, orbitals: {list(map(lambda o: o.__str__(), self.orbitals))})"

class Hero:
    """ Class representing the player """
    def __init__(self):
        self.callsign:str
        self.faction:str
        self.token:str
        self.debug:bool = False
        self.contracts:list[Contract]
        self.headquarter_waypoints:list[Waypoint]
        self.headquarter:Location
        self.headquarter_shipyard:Waypoint
        self.account_id:str
        self.credits:int
        self.api:Spacetrader
        self.ships:list[Ship]

    def __str__(self) -> str:
        return f"Hero(callsign: {self.callsign}\nfaction: {self.faction}\ntoken: {self.token}\ndebug: {self.debug})"

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
        self.ships = list(map(lambda s: Ship(self.api, s), info))
        if self.debug:
            print("Get my ships")
            print(info)
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

    def orbit(self, name:str) -> None:
        """ orbit the ship with the matching name """
        matching = self._find_ship_by_name(name)
        if matching is not None:
            if self.debug:
                print("Orbit")
            matching.orbit()

    def fly(self, ship_name:str, destination_waypoint_symbol:str) -> None:
        """ fly the particular ship with the matching name """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("Fly")
            matching.fly(destination_waypoint_symbol)

    def dock(self, ship_name:str) -> None:
        """ Dock ship """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("Dock")
            matching.dock()

    def refuel(self, ship_name:str) -> None:
        """ Refuel ship """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("Refuel")
            matching.refuel()

    def mine(self, ship_name:str) -> None:
        """ Mine ship """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("Mine")
            matching.mine()

    def get_cargo(self, ship_name:str) -> ShipCargo|None:
        """ Get cargo on ship """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("Get Cargo")
            matching.get_cargo()
            return matching.cargo
        return None

    def view_market(self, ship_name:str) -> dict:
        """ View market """
        """ FIXME, turn dict into object """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            if self.debug:
                print("View Market")
            return matching.view_market()
        return {}

    def sell_all_cargo(self, ship_name:str, except_symbols:list[str] = []) -> None:
        """ Sell all cargo """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            matching.sell_all_cargo(except_symbols)

    def cargo_is_full(self, ship_name:str) -> bool:
        """ See if cargo is full """
        matching = self._find_ship_by_name(ship_name)
        if matching is not None:
            return matching.cargo_is_full()
        return False

    def sell_all_cargo_for_ships(self, ship_names:list[str], goods_to_keep:list[str]) -> None:
        """ Sell all cargo for ships """
        for s in ship_names:
            self.dock(s)
            self.sell_all_cargo(s, goods_to_keep)
        self.get_my_ships()  # refresh ship data

    def send_ships_to_mine(self, ship_names:list[str]) -> None:
        """ Send all ships to mine """
        ship_name_to_done:dict[str, bool] = {}
        for s in ship_names:
            self.orbit(s)
            ship_name_to_done[s] = False

        done:bool = False
        while not done:
            done = True
            for s in ship_names:
                # not done yet
                if self.debug:
                    print(f"{s} done?: {ship_name_to_done[s]}")
                if not ship_name_to_done[s]:
                    if self.debug:
                        print(f"{s} full?: {self.cargo_is_full(s)}")
                    if self.cargo_is_full(s):
                        # full, we are done
                        ship_name_to_done[s] = True
                    else:
                        done = False  # must wait for this mine to finish
                        self.mine(s)
                else:
                    if self.debug:
                        print(f"{s} is done")
            if not done:
                sleep(100)
            self.get_my_ships()  # refresh ship data

    ## Helpers
    def _find_ship_by_name(self, name:str) -> Ship|None:
        all_matching = list(filter(lambda s: s.symbol == name, self.ships))
        if len(all_matching) > 0:
            return all_matching[0]
        else:
            return None
