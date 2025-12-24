import yaml
from collections import deque
from tabulate import tabulate
from dataclasses import dataclass
from enum import Enum
from inquirer import prompt, List as IList
from models.hero import Hero
from models.agent import Agent
from models.system import System
from models.waypoint import Waypoint
from models.ship import Ship

@dataclass
class Option:
  """ Option """
  text:str
  next_choice_name:str

class ChoiceType(Enum):
    PROMPT = 1
    ACTION = 2

@dataclass(init=False)
class Choice:
    """ Choice """
    name:str
    choice_type:ChoiceType
    text:str
    options:list[Option]
    route:str
    next_choice_name:str

    def __init__(self, name:str, choice_type:ChoiceType):
        self.name = name
        self.choice_type = choice_type
        self.text = ""
        self.route = ""
        self.next_choice_name = ""
        self.options = []

    def is_root(self) -> bool:
        return self.name == "root"

class Menu:
    """ Menu Handler """
    def __init__(self, hero:Hero) -> None:
        self.hero = hero
        self.choice_by_name:dict[str,Choice] = {}
        # default exit choice
        self.current_choice:Choice = Choice("quit", ChoiceType.ACTION)
        self.choices:deque[Choice] = deque()

    def init_from_file(self, filename:str):
        with open(filename, "r") as stream:
            try:
                top = yaml.safe_load(stream)
                for obj in top["choices"]:
                    choice:Choice = Choice(obj["name"], ChoiceType[obj["type"].upper()])
                    choice.text = obj.get("text", "")
                    choice.options = list(map(lambda o: Option(o["text"], o["next"]), obj.get("options", [])))
                    choice.next_choice_name = obj.get("next", "")
                    choice.route = obj.get("route", "")
                    self.choice_by_name[choice.name] = choice
                # root and quit are a required node
                # action needs route
                self.current_choice = self.choice_by_name["root"]
                print(self.current_choice)
            except yaml.YAMLError as exc:
                print(exc)
                print(f"Unable to read from file named {filename}")

    def ask_with_choice(self, question:str, choices:list[str], variable_name:str="answer") -> str:
        """ Ask user for a choice """
        questions:list[IList] = [
          IList(variable_name, message=question, choices=choices)
        ]
        answers = prompt(questions)
        if answers is None:
            return ""
        return answers[variable_name]

    def print_dict(self, table: dict[str,str]) -> None:
        """ Print dictionary """
        new_table:dict[str, list[str]] = {}
        for key, value in table.items():
            new_table[key] = [value]
        print(tabulate(new_table, "keys", tablefmt="simple_grid"))

    def print_list(self, table: dict[str,list[str]]) -> None:
        """ Print list """
        print(tabulate(table, "keys", tablefmt="simple_grid"))

    def advance_current_choice(self, the_next_name:str|None=None) -> None:
        if the_next_name is None:
            the_next_name = self.current_choice.next_choice_name
        self.current_choice = self.choice_by_name[the_next_name]

    def back_current_choice(self) -> None:
        if self.current_choice is None:
            return
        self.current_choice = self.choices.pop()
        # keep popping until we get a prompt type
        while self.current_choice.choice_type != ChoiceType.PROMPT:
            self.current_choice = self.choices.pop()

    def reset_choices(self) -> None:
        self.choices.clear()

    def print_waypoints(self, waypoints:list[Waypoint]):
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

    def query_user(self) -> bool:
        """ True to keep going, False to quit """
        if self.current_choice is not None:
            if self.current_choice.is_root():
                self.reset_choices()
            self.choices.append(self.current_choice)
            match self.current_choice.choice_type:
                case ChoiceType.PROMPT:
                    choice:str = self.ask_with_choice(
                            self.current_choice.text,
                            list(map(lambda x: x.text, self.current_choice.options)))
                    matching:Option = next(
                            (n for n in self.current_choice.options if n.text == choice), Option("", "root"))
                    self.advance_current_choice(matching.next_choice_name)
                    return choice != "quit"
                case ChoiceType.ACTION:
                    match self.current_choice.route:
                        case "get_agent":
                            agent:Agent = self.hero.get_agent()
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
                        case "get_systems":
                            systems:list[System] = self.hero.get_systems()
                            names:list[str] = []
                            constellations:list[str] = []
                            xs:list[str] = []
                            ys:list[str] = []
                            symbols:list[str] = []
                            sectors:list[str] = []
                            types:list[str] = []
                            factions:list[str] = []
                            for system in systems:
                                names.append(system.name)
                                constellations.append(system.constellation)
                                xs.append(str(system.x))
                                ys.append(str(system.y))
                                symbols.append(system.symbol)
                                types.append(system.system_type)
                                sectors.append(system.sector)
                                factions.append(", ".join(system.factions))
                            pretty_systems:dict[str,list[str]] = {
                                "Names": names,
                                "Constellations": constellations,
                                "X": xs,
                                "Y": ys,
                                "Symbols": symbols,
                                "Sectors": sectors,
                                "Types": types,
                                "Factions": factions,
                            }
                            self.print_list(pretty_systems)
                        case "get_headquarter":
                            hq:Waypoint = self.hero.get_headquarter()
                            self.print_list({
                                "Fields": [
                                    "Waypoint",
                                    "Type",
                                    "(X, Y)",
                                    "Orbital",
                                    "Traits",
                                ],
                                "Value": [
                                    str(hq.waypoint),
                                    hq.type,
                                    f"({hq.x}, {hq.y})",
                                    ", ".join(list(map(lambda w: w.waypoint, hq.orbitals))),
                                    ", ".join(list(map(lambda w: w.symbol, hq.traits))),
                                ]
                            })
                        case "get_headquarter_waypoints":
                            self.print_waypoints(self.hero.get_headquarter_waypoints())
                        case "get_ships":
                            self.hero.get_my_ships()
                            names:list[str] = []
                            systems:list[str] = []
                            status:list[str] = []
                            flight_mode:list[str] = []
                            fuel:list[str] = []
                            for name, ship in self.hero.ships_by_symbol.items():
                                names.append(name)
                                systems.append(ship.nav.system)
                                status.append(ship.nav.status)
                                flight_mode.append(ship.nav.flight_mode)
                                fuel.append(f"{ship.fuel.current} / {ship.fuel.capacity}"),
                            self.print_list({
                                "Names": names,
                                "Current System": systems,
                                "Status": status,
                                "Flight Mode": flight_mode,
                                "Fuel": fuel,
                            })
                            ship_name:str = self.ask_with_choice("Which ship do you want to view?", names)
                            ship:Ship = self.hero.ships_by_symbol[ship_name]
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
                        case "get_contracts":
                            contracts = self.hero.get_contracts()
                            contract_ids = list(map(lambda c: c.id, contracts))
                            if len(contracts) == 0:
                                print("No contracts")
                            else:
                                self.print_list({"Contract IDs": contract_ids})
                                contract_id:str = self.ask_with_choice("Which contract do you want to view?", contract_ids)
                                contract:Contract|None = self.hero.get_contract_by_id(contract_id)
                                if contract is None:
                                    print("Contract not found")
                                else:
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
                                    if not contract.accepted:
                                        match self.ask_with_choice("Do you want to accept contract?", ["yes", "no"]):
                                            case "yes":
                                                self.hero.accept_contract(contract_id)
                                                print("Accepted!")
                        case "get_waypoints":
                            system_names:list[str] = list(map(lambda s: s.name, self.hero.systems))
                            cancel_text:str = "back"
                            system_names.insert(0, cancel_text)
                            system:str = self.ask_with_choice("Want waypoints?", system_names)
                            if system == cancel_text:
                                self.back_current_choice()
                                return True

                            matching:System|None = next((s for s in self.hero.systems if s.name == system), None)
                            if matching is None:
                                print("Unable to find matching system.")
                            else:
                                self.print_waypoints(self.hero.get_waypoints(matching.symbol))

                    self.advance_current_choice()
                    return True
        return False

