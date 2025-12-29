from dataclasses import dataclass
from datetime import datetime as dt

@dataclass
class Account:
    """ Account """
    id:str
    email:str
    token:str
    created_at:dt
