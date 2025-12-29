from yaml import dump, safe_load, YAMLError
from time import sleep
from models.ship import Ship, ShipCargo
from models.waypoint import Waypoint
from models.location import Location
from models.spacetrader import Spacetrader
from models.contract import Contract
from models.agent import Agent
from models.system import System
from models.shipyard import Shipyard
from models.account import Account
from datetime import datetime

class Hero:
    """ Class representing the player """
    def __init__(self):
        self.callsign:str = ""
        self.faction:str = ""
        self.token:str = ""
        self.debug:bool = False
        self.contracts:list[Contract] = []
        self.agent:Agent|None = None
        self.headquarter_waypoints:list[Waypoint] = []
        self.headquarter:Location|None = None
        self.headquarter_shipyard:Waypoint|None = None
        self.account_id:str = ""
        self.credits:int = 0
        self.api:Spacetrader = Spacetrader("", "")
        self.ships_by_symbol:dict[str, Ship] = {}
        self.systems:list[System] = []

    def __str__(self) -> str:
        return f"Hero(callsign: {self.callsign}, faction: {self.faction})"

    def init_from_file(self, filename:str):
        """ Read input file and build everything """
        with open(filename, "r") as stream:
            try:
                obj = safe_load(stream)
                self.callsign = obj["callsign"]
                self.faction = obj["faction"]
                self.token = obj.get("token", None)
                self.account_token = obj.get("account_token", None)
                self.debug = obj.get("debug", False)
                self.api = Spacetrader(self.token, self.account_token, self.debug)
                self.headquarter = None
                if self.debug:
                    print(f"init_from_file: {filename}")
                    print(self)
            except YAMLError as exc:
                print(exc)
                print(f"Unable to read from file named {filename}")

        account:Account|None = self.get_account()
        if account is None:
            self.token = ""
            self.api.token = ""

        # check for token
        if self.token is None or self.token == "":
            if self.debug:
                print("No token")
            if self.account_token is None or self.account_token == "":
                raise Exception("No valid token nor account token found")

            resp = self.api.post_noauth("register", {"symbol": self.callsign, "faction": self.faction})
            if self.debug:
                print("Response from register")
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
                                 "token": self.token,
                                 "account_token": self.account_token
                               }
                        stream.write(dump(data))
                    except YAMLError as exc:
                        print(exc)
                        print(f"Unable to write to file named {filename}")
            else:
                print("Unable to get token")

    def get_account(self) -> Account|None:
        """ Get account """
        try:
            account_dict = self.api.get_auth("my/account")["data"]["account"]
            if self.debug:
                print("get_account")
                print(account_dict)
            return Account(
                    account_dict.get("id", ""),
                    account_dict.get("email", ""),
                    account_dict.get("token", ""),
                    account_dict.get("createdAt", None)
            )
        except Exception as e:
            print(e)
            return None

    def get_agent(self, lazy_load:bool=False) -> Agent:
        """ Get agent info """
        if self.debug:
            print(f"get_agent, lazy_load: {lazy_load}")
        if (not lazy_load) or (lazy_load and self.agent is None):
            info = self.api.get_auth("my/agent")["data"]
            self.agent:Agent = Agent(
                    info["accountId"],
                    info["symbol"],
                    Location(info["headquarters"]),
                    info["credits"],
                    info["startingFaction"],
                    info["shipCount"],
            )
            if self.debug:
                print(self.agent)
        self.headquarter = self.agent.headquarter
        self.account_id = self.agent.account_id
        self.credits = self.agent.credits
        return self.agent

    def get_my_ships(self) -> list[Ship]:
        """ Get my ships """
        info = self.api.get_auth("my/ships")["data"]
        ships = list(map(lambda s: Ship(self.api, s), info))
        ship_keys = list(map(lambda s: s.symbol, ships))
        self.ships_by_symbol = dict(zip(ship_keys, ships))
        if self.debug:
            print("Get my ships")
            print(info)
            for s in self.ships_by_symbol:
                print(s)
        return ships

    def get_contracts(self, lazy_load:bool=False) -> list[Contract]:
        """ Get contracts """
        if (not lazy_load) or (lazy_load and len(self.contracts) == 0):
            info = self.api.get_auth("my/contracts")["data"]
            self.contracts = list(map(lambda c: Contract(c), info))
            if self.debug:
                print("Get Contracts")
                for c in self.contracts:
                    print(c)
        return self.contracts

    def get_contract_by_id(self, id) -> Contract|None:
        """ Get contract by id """
        self.get_contracts(True)
        if len(self.contracts) == 0:
            return None
        return next((c for c in self.contracts if c.id == id), None)

    def accept_all_contracts(self) -> None:
        """ Accept all contracts """
        self.get_contracts()
        for c in self.contracts:
            self.accept_contract(c.id)
        self.get_contracts()

    def accept_contract(self, contract_id:str) -> None:
        """ Accept a particular contract """
        info = self.api.post_auth(f"my/contracts/{contract_id}/accept")
        if self.debug:
            print("Accept Contract")
            print(info)

    def get_headquarter_waypoints(self, page:int=1) -> list[Waypoint]:
        """ Get all the waypoints in the same system as the headquarter """
        self.get_agent(True)
        if self.headquarter is None:
            return []
        return self.get_waypoints(self.headquarter.system, page)

    def get_waypoints(self, system:str, trait:str="", page:int=1) -> list[Waypoint]:
        """ Get all the waypoints given a system """
        url:str = f"systems/{system}/waypoints"
        params:str = ""
        if trait:
            params = f"traits={trait}"
        if page:
            if params:
                params = f"{params}&page={page}"
            else:
                params = f"page={page}"
        url = f"{url}?{params}"
        if self.debug:
            print(url)
        raw_waypoints = self.api.get_auth(url)["data"]
        waypoints:list[Waypoint] = list(map(lambda w: Waypoint(w), raw_waypoints))
        if self.debug:
            print(f"Get waypoints for system {system} and trait {trait}")
            for w in waypoints:
                print(w)
        return waypoints

    def get_shipyard_waypoints(self, system:str, page:int=1) -> list[Waypoint]:
        """ Get all the shipyard waypoints given a system """
        return self.get_waypoints(system, "SHIPYARD", page)

    def get_market_waypoints(self, system:str, page:int=1) -> list[Waypoint]:
        """ Get all the market waypoints given a system """
        return self.get_waypoints(system, "MARKETPLACE", page)

    def get_headquarter_shipyard_waypoints(self, page:int=1) -> list[Waypoint]:
        """ Get all the shipyard waypoints in HQ """
        self.get_agent(True)
        return self.get_shipyard_waypoints(self.headquarter.system, page)

    def get_headquarter_market_waypoints(self, page:int=1) -> list[Waypoint]:
        """ Get all the market waypoints in HQ """
        self.get_agent(True)
        return self.get_market_waypoints(self.headquarter.system, page)

    def get_headquarter(self) -> Waypoint:
        """ Get the waypoint that represents the headquarter """
        self.get_agent(True)
        return self.get_waypoint(self.headquarter)

    def get_systems(self) -> list[System]:
        """ Get all systems """
        raw = self.api.get_auth(f"systems")["data"]
        if self.debug:
            print("Get Systems")
            print(raw)
        self.systems = list(map(lambda s: System(s), raw))
        return self.systems

    def get_system(self, system_symbol:str) -> System:
        """ Get single system by system symbol """
        raw = self.api.get_auth(f"systems/{system_symbol}")["data"]
        if self.debug:
            print("Get System")
            print(raw)
        return System(raw)

    def get_waypoint(self, location) -> Waypoint:
        """ Get waypoint given a location """
        raw_waypoint = self.api.get_auth(f"systems/{location.system}/waypoints/{location.waypoint}")["data"]
        if self.debug:
            print("Get Waypoint")
            print(raw_waypoint)
        return Waypoint(raw_waypoint)

    def get_shipyard(self, shipyard_waypoint_symbol:str) -> Shipyard|None:
        """ Get all the ships available to purchase from headquarter """
        system:str = "-".join(shipyard_waypoint_symbol.split("-")[0:2])
        raw = self.api.get_auth(f"systems/{system}/waypoints/{shipyard_waypoint_symbol}/shipyard")["data"]
        if self.debug:
            print("Get Shipyard")
            print(raw)
        return Shipyard(raw)

    def buy_ship(self, ship_type:str="SHIP_MINING_DRONE", symbol:str="") -> dict:
        """ Buy ship type at given symbol """
        raw_purchase = {}

        if symbol == "" and self.headquarter_shipyard is not None and self.headquarter_shipyard.waypoint is not None:
            # set to headquarter if not set
            symbol = self.headquarter_shipyard.waypoint

        raw_purchase = self.api.post_auth(f"my/ships", {
            "shipType": ship_type,
            "waypointSymbol": symbol,
        })["data"]
        if self.debug:
            print(f"Buy Ship, type:{ship_type}, symbol: {symbol}")
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
        # FIXME: turn dict into object
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
        return self.ships_by_symbol.get(name, None)

