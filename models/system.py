from models.waypoint import Waypoint

class System():
    """ The system """
    def __init__(self, system:dict) -> None:
        self.name:str = system["name"]
        self.constellation:str = system["constellation"]
        self.symbol:str = system["symbol"]
        self.sector:str = system["sectorSymbol"]
        self.system_type:str = system["type"]
        self.x:int = system["x"]
        self.y:int = system["y"]
        self.waypoints:list[Waypoint] = list(map(lambda w: Waypoint(w), system["waypoints"]))
        self.factions:list[str] = list(map(lambda f: f["symbol"], system["factions"]))

    def __str__(self) -> str:
        return f"System(name: {self.name}, constellation: {self.constellation}, x: {self.x}, y: {self.y}, symbol: {self.symbol}, sector: {self.sector}, type: {self.system_type}, factions: {self.factions}, waypoints: {list(map(lambda w: str(w), self.waypoints))})"


