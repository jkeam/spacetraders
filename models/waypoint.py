from dataclasses import dataclass
from models.location import Location

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
        self.orbits:str = loc.get("orbits", "")
        self.traits:list[WaypointTrait] = list(map(lambda t: WaypointTrait(t["symbol"], t["name"], t["description"]), loc.get("traits", [])))

    def __str__(self) -> str:
        return f"Waypoint(location: {super().__str__()}, type: {self.type}, x: {self.x}, y: {self.y}, orbitals: {list(map(lambda o: o.__str__(), self.orbitals))})"
