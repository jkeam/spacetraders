from tabulate import tabulate
from models.waypoint import Waypoint
from models.ship import Ship, ShipExtraction, ShipCooldown, ShipCargo, ShipMount, ShipModule, Market, ShipNav
from models.shipyard import Shipyard
from models.contract import Contract
from models.agent import Agent
from models.system import System

class Printer():
    def __init__(self, debug:bool) -> None:
        self.debug = debug

    def print_dict(self, table: dict[str,str]) -> None:
        """ Print dictionary """
        new_table:dict[str, list[str]] = {}
        for key, value in table.items():
            new_table[key] = [value]
        print(tabulate(new_table, "keys", tablefmt="simple_grid"))

    def print_list(self, table: dict[str,list[str]]) -> None:
        """ Print list """
        print(tabulate(table, "keys", tablefmt="simple_grid"))

    def print_simple_list(self, header:str, the_list:list[str]) -> None:
        the_obj:dict[str, list[str]] = {}
        the_obj[header] = the_list
        self.print_list(the_obj)

    def print_waypoints(self, waypoints:list[Waypoint], distances:list[float]=[]) -> None:
        """ Format and print waypoints """
        ways:list[str] = []
        types:list[str] = []
        xys:list[str] = []
        orbitals:list[str] = []
        traits:list[str] = []
        for waypoint in waypoints:
            ways.append(str(waypoint.waypoint))
            types.append(waypoint.type)
            xys.append(f"{str(waypoint.x)}, {str(waypoint.y)}")
            orbitals.append("\n".join(list(map(lambda w: w.waypoint, waypoint.orbitals))))
            traits.append("\n".join(list(map(lambda w: w.symbol, waypoint.traits))))
        pretty_waypoints:dict[str,list[str]] = {
            "Waypoint": ways,
            "Type": types,
            "X, Y": xys,
            "Orbital": orbitals,
            "Traits": traits
        }
        if len(distances) > 0:
            pretty_waypoints["Distance"] = list(map(lambda x: str(x), distances))
        self.print_list(pretty_waypoints)

    def print_ships(self, ships:list[Ship]) -> None:
        """ Print listing of ships, but short """
        names:list[str] = []
        systems:list[str] = []
        status:list[str] = []
        flight_mode:list[str] = []
        fuel:list[str] = []
        roles:list[str] = []
        for ship in ships:
            names.append(ship.name)
            systems.append(ship.nav.system)
            status.append(ship.nav.status)
            flight_mode.append(ship.nav.flight_mode)
            fuel.append(f"{ship.fuel.current} / {ship.fuel.capacity}")
            roles.append(ship.role)
        self.print_list({
            "Names": names,
            "Current System": systems,
            "Status": status,
            "Flight Mode": flight_mode,
            "Fuel": fuel,
            "Role": roles,
        })

    def print_ship(self, ship:Ship) -> None:
        self.print_list({
            "Field": [
                "Name",
                "Symbol",
                "Faction",
                "Role",
                "Crew",
                "Fuel",
                "Frame",
                "Current System",
                "Current Status",
                "Flight Mode",
                "Departure",
                "Arrival",
            ],
            "Value": [
                ship.name,
                ship.symbol,
                ship.faction,
                ship.role,
                f"{ship.crew.current} / {ship.crew.capacity}, required={ship.crew.required}, rotation={ship.crew.rotation}, morale={ship.crew.morale}, wages={ship.crew.wages}",
                f"{ship.fuel.current} / {ship.fuel.capacity}",
                f"{ship.frame.name} ({ship.frame.symbol}): condition={ship.frame.condition}, power_req={ship.frame.power_requirement}, crew_req={ship.frame.crew_requirement}, module_slots={ship.frame.module_slots}, mounting_points={ship.frame.mounting_points}",
                ship.nav.system,
                ship.nav.status,
                ship.nav.flight_mode,
                f"{ship.nav.route.departure.type} at {ship.nav.route.departure.symbol} ({ship.nav.route.departure.x}, {ship.nav.route.departure.y}) at {ship.nav.route.departure_at}",
                f"{ship.nav.route.destination.type} at {ship.nav.route.destination.symbol} ({ship.nav.route.destination.x}, {ship.nav.route.destination.y}) at {ship.nav.route.arrival_at}",
            ],
        })
        print("Cargo")
        self.print_cargo(ship.cargo)
        print("Modules")
        self.print_modules(ship.modules)
        print("Mounts")
        self.print_mounts(ship.mounts)

    def print_contract(self, contract:Contract) -> None:
        if self.debug:
            print(contract)
        self.print_list({
            "Field": [
                "ID",
                "Faction",
                "Type",
                "Accepted",
                "Fulfilled",
                "Deadline",
                "Deadline To Accept",
                "Payment on Accepted",
                "Payment on Fulfilled",
                "Deliveries",
            ],
            "Value": [
                contract.id,
                contract.faction,
                contract.type,
                str(contract.accepted),
                str(contract.fulfilled),
                str(contract.terms.deadline),
                str(contract.deadline_to_accept),
                str(contract.terms.payment_on_accepted),
                str(contract.terms.payment_on_fulfilled),
                ", ".join(list(map(lambda d: f"{d.units_fulfilled} / {d.units_required} of {d.trade} to {d.destination}", contract.terms.deliveries))),
            ]
        })

    def print_agent(self, agent:Agent) -> None:
        self.print_list({
            "Field": [
                "Account ID",
                "Symbol",
                "Headquarter",
                "Credits",
                "Starting Faction",
                "Ship Count",
            ],
            "Value": [
                agent.account_id,
                agent.symbol,
                agent.headquarter.waypoint,
                str(agent.credits),
                agent.starting_faction,
                str(agent.ship_count),
            ]
        })

    def print_system(self, system:System) -> None:
        self.print_systems([system])

    def print_systems(self, systems:list[System]) -> None:
        names:list[str] = []
        constellations:list[str] = []
        xy:list[str] = []
        symbols:list[str] = []
        sectors:list[str] = []
        types:list[str] = []
        factions:list[str] = []
        for system in systems:
            names.append(system.name)
            constellations.append(system.constellation)
            xy.append(f"({str(system.x)}, {str(system.y)})")
            symbols.append(system.symbol)
            types.append(system.system_type)
            sectors.append(system.sector)
            factions.append(", ".join(system.factions))
        pretty_systems:dict[str,list[str]] = {
            "Names": names,
            "Constellations": constellations,
            "(X, Y)": xy,
            "Symbols": symbols,
            "Sectors": sectors,
            "Types": types,
            "Factions": factions,
        }
        self.print_list(pretty_systems)

    def print_waypoint(self, hq:Waypoint) -> None:
        self.print_waypoints([hq])

    def print_modules(self, modules:list[ShipModule]) -> None:
        names:list[str] = []
        symbols:list[str] = []
        capacity:list[str] = []
        power:list[str] = []
        crew:list[str] = []
        slot:list[str] = []
        description:list[str] = []
        for m in modules:
            names.append(m.name)
            symbols.append(m.symbol)
            capacity.append(m.capacity)
            power.append(m.power_requirement)
            crew.append(m.crew_requirement)
            slot.append(m.slot_requirement)
            description.append(m.description)
        self.print_list({
            "Names": names,
            "Symbols": symbols,
            "Capacity": capacity,
            "Power Req": power,
            "Crew Req": crew,
            "Slot Req": slot,
        })
        print("Descriptions")
        for index, desc in enumerate(description):
            print(f"{names[index]}: {desc}")

    def print_mounts(self, modules:list[ShipMount]) -> None:
        names:list[str] = []
        symbols:list[str] = []
        power:list[str] = []
        crew:list[str] = []
        strength:list[str] = []
        description:list[str] = []
        for m in modules:
            names.append(m.name)
            symbols.append(m.symbol)
            power.append(str(m.power_requirement))
            crew.append(str(m.crew_requirement))
            strength.append(str(m.strength))
            description.append(m.description)
        self.print_list({
            "Names": names,
            "Symbols": symbols,
            "Power Req": power,
            "Crew Req": crew,
            "Strength": strength,
        })
        print("Descriptions")
        for index, desc in enumerate(description):
            print(f"{names[index]}: {desc}")

    def print_cargo(self, cargo:ShipCargo) -> None:
        names:list[str] = []
        symbols:list[str] = []
        units:list[str] = []
        print(f"Cargo: {cargo.units} / {cargo.capacity}")
        for c in cargo.inventory:
            names.append(c.name)
            symbols.append(c.symbol)
            units.append(str(c.units))
        self.print_list({
            "Names": names,
            "Symbols": symbols,
            "Units": units,
        })

    def print_extraction_results(self, extraction:ShipExtraction, cooldown:ShipCooldown, cargo:ShipCargo) -> None:
        """ Print extraction results """
        self.print_list({
            "Field": [
                "Ship",
                "Element",
                "Units",
                "Cooldown(s)",
                "Ready",
                "Capacity",
                "Used",
            ], "Values": [
                extraction.ship_symbol,
                extraction.yield_symbol,
                str(extraction.yield_units),
                str(cooldown.total_seconds),
                str(cooldown.expiration),
                str(cargo.capacity),
                str(cargo.units),
            ]})

    def print_import_export_exchange(self, title:str, the_list:list) -> None:
        print(title)
        if len(the_list) == 0:
            print("[]")
            return

        names:list[str] = []
        symbols:list[str] = []
        for c in the_list:
            names.append(c.name)
            symbols.append(c.symbol)
        self.print_list({
            "Name": names,
            "Symbol": symbols,
        })

    def print_market(self, market:Market) -> None:
        # transactions:list[Transaction]
        print(f"Market at {market.symbol}")

        print("Goods")
        symbols:list[str] = []
        trade_types:list[str] = []
        volumes:list[str] = []
        supplies:list[str] = []
        purchase_prices:list[str] = []
        sell_prices:list[str] = []

        if len(market.trade_goods) == 0:
            print("[]")
        else:
            for c in market.trade_goods:
                symbols.append(c.symbol)
                trade_types.append(c.trade_type)
                volumes.append(str(c.volume))
                supplies.append(c.supply)
                purchase_prices.append(str(c.purchase_price))
                sell_prices.append(str(c.sell_price))
            self.print_list({
                "Symbol": symbols,
                "Type": trade_types,
                "Volume": volumes,
                "Supply": supplies,
                "Purchase Price": purchase_prices,
                "Sell Price": sell_prices,
            })

        self.print_import_export_exchange("Exports", market.exports)
        self.print_import_export_exchange("Imports", market.imports)
        self.print_import_export_exchange("Exchanges", market.exchanges)

        print("Transactions")
        waypoint_symbols:list[str] = []
        ship_symbols:list[str] = []
        trade_symbols:list[str] = []
        transaction_types:list[str] = []
        units:list[str] = []
        price_per_units:list[str] = []
        total_prices:list[str] = []
        bought_ats:list[str] = []
        if len(market.transactions) == 0:
            print("[]")
        else:
            for c in market.transactions:
                waypoint_symbols.append(c.waypoint_symbol)
                ship_symbols.append(c.ship_symbol)
                trade_symbols.append(c.trade_symbol)
                transaction_types.append(c.transaction_type)
                units.append(str(c.units))
                price_per_units.append(str(c.price_per_unit))
                total_prices.append(str(c.total_price))
                bought_ats.append(str(c.bought_at))
            self.print_list({
                "Waypoint Symbol": waypoint_symbols,
                "Ship Symbol": ship_symbols,
                "Trade Symbol": trade_symbols,
                "Transaction Type": transaction_types,
                "Unit": units,
                "Price per Unit": price_per_units,
                "Total Price": total_prices,
                "Bought At": bought_ats,
            })

    def print_nav(self, nav:ShipNav) -> None:
        systems:list[str] = [nav.system]
        waypoints:list[str] = [nav.waypoint.waypoint]
        routes:list[str] = [f"{str(nav.route.departure.symbol)} to {str(nav.route.destination.symbol)}"]
        arrival_at:list[str] = [str(nav.route.arrival_at)]
        statuses:list[str] = [nav.status]
        flight_modes:list[str] = [nav.flight_mode]
        self.print_list({
            "System": systems,
            "Waypoint": waypoints,
            "Route": routes,
            "Arrival": arrival_at,
            "Status": statuses,
            "Flight Mode": flight_modes
        })

    def print_shipyard(self, shipyard:Shipyard) -> None:
        self.print_list({
            "Field": [
                "Symbol",
                "Modifications Fee",
                "Ship Types",
            ],
            "Values": [
                shipyard.symbol,
                str(shipyard.modifications_fee),
                "\n".join(shipyard.ship_types),
            ]
        })
