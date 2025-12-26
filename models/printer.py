from tabulate import tabulate
from models.waypoint import Waypoint
from models.ship import Ship
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

    def print_waypoints(self, waypoints:list[Waypoint]) -> None:
        """ Format and print waypoints """
        ways:list[str] = []
        types:list[str] = []
        xs:list[str] = []
        ys:list[str] = []
        orbitals:list[str] = []
        traits:list[str] = []
        for waypoint in waypoints:
            ways.append(str(waypoint.waypoint))
            types.append(waypoint.type)
            xs.append(str(waypoint.x))
            ys.append(str(waypoint.y))
            orbitals.append(", ".join(list(map(lambda w: w.waypoint, waypoint.orbitals))))
            traits.append(", ".join(list(map(lambda w: w.symbol, waypoint.traits))))
        pretty_waypoints:dict[str,list[str]] = {
            "Waypoint": ways,
            "Type": types,
            "X": xs,
            "Y": ys,
            "Orbital": orbitals,
            "Traits": traits
        }
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
                "Cargo",
                "Fuel",
                "Frame",
                "Current System",
                "Current Status",
                "Flight Mode",
                "Departure",
                "Arrival",
                "Modules",
                "Mounts",
            ],
            "Value": [
                ship.name,
                ship.symbol,
                ship.faction,
                ship.role,
                f"{ship.crew.current} / {ship.crew.capacity}, required={ship.crew.required}, rotation={ship.crew.rotation}, morale={ship.crew.morale}, wages={ship.crew.wages}",
                f"{ship.cargo.units} / {ship.cargo.capacity}, inventory=[{', '.join(list(map(lambda i: str(i), ship.cargo.inventory)))}]",
                f"{ship.fuel.current} / {ship.fuel.capacity}",
                f"{ship.frame.name} ({ship.frame.symbol}): condition={ship.frame.condition}, power_req={ship.frame.power_requirement}, crew_req={ship.frame.crew_requirement}, module_slots={ship.frame.module_slots}, mounting_points={ship.frame.mounting_points}",
                ship.nav.system,
                ship.nav.status,
                ship.nav.flight_mode,
                f"{ship.nav.route.departure.type} at {ship.nav.route.departure.symbol} ({ship.nav.route.departure.x}, {ship.nav.route.departure.y}) at {ship.nav.route.departure_at}",
                f"{ship.nav.route.destination.type} at {ship.nav.route.destination.symbol} ({ship.nav.route.destination.x}, {ship.nav.route.destination.y}) at {ship.nav.route.arrival_at}",
                "\n\n".join(list(map(lambda m: f"{m.name} ({m.symbol}): capacity={m.capacity}, power_req={m.power_requirement}, crew_req={m.crew_requirement}, slot_req={m.slot_requirement},\n{m.description}", ship.modules))),
                "\n\n".join(list(map(lambda m: f"{m.name} ({m.symbol}): power_req={m.power_requirement}, crew_req={m.crew_requirement}, strength={m.strength},\n{m.description}", ship.mounts))),
            ],
        })

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
                "Expiration",
                "Deadline",
                "Term Deadline",
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
                str(contract.expiration),
                str(contract.deadline),
                str(contract.terms.deadline),
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
