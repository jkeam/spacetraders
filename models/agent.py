from dataclasses import dataclass
from models.location import Location

@dataclass
class Agent:
    """ Agent """
    account_id:str
    symbol:str
    headquarter:Location
    credits:int
    starting_faction:str
    ship_count:int
