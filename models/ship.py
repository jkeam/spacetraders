from datetime import datetime as dt
from dataclasses import dataclass
from models.location import Location
from models.spacetrader import Spacetrader

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

@dataclass
class ShipNav:
    """ Ship Nav """
    system:str
    waypoint:Location
    route:ShipRoute
    status:str
    flight_mode:str

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

@dataclass
class ShipCargo:
    """ Ship cargo """
    capacity:int
    units:int
    inventory:list[ShipCargoItem]

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
    """ Ship frame """
    symbol:str
    name:str
    description:str
    module_slots:int
    mounting_points:int
    fuel_capacity:int
    condition:int
    power_requirement:int
    crew_requirement:int

@dataclass
class ShipReactor:
    """ Ship reactor """
    symbol:str
    name:str
    description:str
    condition:int
    power_output:int
    crew_requiremen:int

@dataclass
class ShipEngine:
    """ Ship engine """
    symbol:str
    name:str
    description:str
    condition:int
    speed:int
    power_requirement:int
    crew_requirement:int

@dataclass
class ShipModule:
    """ Ship module """
    symbol:str
    name:str
    description:str
    capacity:int
    power_requirement:int
    crew_requirement:int
    slot_requirement:int

@dataclass
class ShipMount:
    """ Ship mount """
    symbol:str
    name:str
    description:str
    strength:int
    power_requirement:int
    crew_requirement:int

class Ship:
    """ Ship """
    def __init__(self, api:Spacetrader, ship:dict[str, any]) -> None:
        self.api = api
        self.name:str = ship.get("name", "")
        self.faction:str = ship.get("factionSymbol", "")
        self.role:str = ship.get("role", "")

        registration:dict[str, str] = ship.get("registration", {})
        if registration:
            self.name:str = registration.get("name", "")
            self.faction:str = registration.get("factionSymbol", "")
            self.role:str = registration.get("role", "")

        self.symbol:str = ship["symbol"]
        self.nav = self._create_nav(ship["nav"])
        self.crew = ShipCrew(
                ship["crew"]["current"],
                ship["crew"]["capacity"],
                ship["crew"]["required"],
                ship["crew"]["rotation"],
                ship["crew"]["morale"],
                ship["crew"]["wages"])

        self.cargo = ShipCargo(
                ship["cargo"]["capacity"],
                ship["cargo"]["units"],
                list(map(lambda i: ShipCargoItem(i["symbol"], i["name"], i["description"], i["units"]), ship["cargo"]["inventory"])))

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

        self.reactor = ShipReactor(
                ship["reactor"]["symbol"],
                ship["reactor"]["name"],
                ship["reactor"]["description"],
                ship["reactor"]["condition"],
                ship["reactor"]["powerOutput"],
                ship["reactor"]["requirements"]["crew"])

        self.engine = ShipEngine(
                ship["engine"]["symbol"],
                ship["engine"]["name"],
                ship["engine"]["description"],
                ship["engine"]["condition"],
                ship["engine"]["speed"],
                ship["engine"]["requirements"]["power"],
                ship["engine"]["requirements"]["crew"])

        self.modules = list(map(lambda m: ShipModule(m["symbol"], m["name"], m["description"], m.get("capacity", 0), m["requirements"]["power"], m["requirements"]["crew"], m["requirements"]["slots"]), ship["modules"]))

        self.mounts = list(map(lambda m: ShipMount(m["symbol"], m["name"], m["description"], m["strength"], m["requirements"]["power"], m["requirements"]["crew"]), ship["mounts"]))

    def __str__(self) -> str:
        return f"Ship(name: {self.name}, faction: {self.faction}, role: {self.role}, symbol: {self.symbol}, nav: {self.nav}, crew: {self.crew}, cargo: {self.cargo}, fuel: {self.fuel}, frame: {self.frame}, modules: {list(map(lambda m: m.__str__(), self.modules))}), mounts: {list(map(lambda m: m.__str__(), self.mounts))})"

    def _create_nav(self, ship_nav:dict) -> ShipNav:
        system:str = ship_nav["systemSymbol"]
        waypoint:Location = Location(ship_nav["waypointSymbol"])

        route:dict = ship_nav["route"]
        departure:ShipPoint = ShipPoint(
                route["origin"]["symbol"],
                route["origin"]["type"],
                route["origin"]["systemSymbol"],
                route["origin"]["x"],
                route["origin"]["y"])
        destination:ShipPoint = ShipPoint(
                route["destination"]["symbol"],
                route["destination"]["type"],
                route["destination"]["systemSymbol"],
                route["destination"]["x"],
                route["destination"]["y"])
        arrival_at = dt.fromisoformat(route["arrival"])
        departure_at = dt.fromisoformat(route["departureTime"])
        ship_route:ShipRoute = ShipRoute(departure, destination, arrival_at, departure_at)

        status:str = ship_nav["status"]
        flight_mode:str = ship_nav["flightMode"]
        return ShipNav(system, waypoint, ship_route, status, flight_mode)

    def is_docked(self) -> bool:
        """ Tells if ship is docked """
        return self.nav.status == "DOCKED"

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

