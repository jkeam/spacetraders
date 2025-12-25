class Location:
    """ Represents a location """
    def __init__(self, coordinate:str) -> None:
        data:list[str] = coordinate.split("-")
        self.sector:str = data[0]
        self.system:str = f"{data[0]}-{data[1]}"
        self.waypoint:str = coordinate

    def __str__(self) -> str:
        return f"Location(sector: {self.sector}, system: {self.system}, waypoint: {self.waypoint})"

