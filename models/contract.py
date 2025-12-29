from dataclasses import dataclass
from datetime import datetime as dt

@dataclass
class ContractDelivery:
    """ The thing to deliver as described in the terms """
    trade:str
    destination:str
    units_required:int
    units_fulfilled:int

@dataclass
class ContractTerm:
    """ Represents the terms of the contract """
    deadline:dt
    payment_on_accepted:int
    payment_on_fulfilled:int
    deliveries:list[ContractDelivery]

class Contract:
    """ Represents a contract """
    def __init__(self, cont:dict) -> None:
        self.id:str = cont["id"]
        self.faction:str = cont["factionSymbol"]
        self.type:str = cont["type"]
        self.terms:ContractTerm = ContractTerm(dt.fromisoformat(cont["terms"]["deadline"]),
                                               cont["terms"]["payment"]["onAccepted"],
                                               cont["terms"]["payment"]["onFulfilled"],
                                               list(map(lambda d: ContractDelivery(d["tradeSymbol"], d["destinationSymbol"], d["unitsRequired"], d["unitsFulfilled"]), cont.get("terms", {}).get("deliver", []))))
        self.accepted:bool = cont["accepted"]
        self.fulfilled:bool = cont["fulfilled"]
        self.deadline_to_accept:dt = dt.fromisoformat(cont["deadlineToAccept"])

    def __str__(self) -> str:
        return f"Contract(id: {self.id}, faction: {self.faction}, type: {self.type}, terms: {self.terms}, accepted: {self.accepted}, fulfilled: {self.fulfilled}, deadline_to_accept: {self.deadline_to_accept})"

