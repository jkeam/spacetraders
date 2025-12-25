class Shipyard:
    """ Shipyard with ships """

    # SHIP_MINING_DRONE

    def __init__(self, from_api:dict[str, any]) -> None:
        self.symbol:str = from_api['symbol']
        self.modifications_fee:int = from_api['modificationsFee']
        self.ship_types:list[str] = []
        for ship_type in from_api["shipTypes"]:
            self.ship_types.append(ship_type["type"])

    def __str__(self) -> str:
        return f"Shipyard(symbol: {self.symbol}, modifications_fee: {self.modifications_fee}, ship_types: {'-'.join(self.ship_types)}"
