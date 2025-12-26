import yaml
from collections import deque
from dataclasses import dataclass
from enum import Enum
from inquirer import prompt, List as IList, Text as IText
from models.hero import Hero
from models.system import System
from models.waypoint import Waypoint
from models.ship import Ship, ShipNav
from models.contract import Contract
from models.printer import Printer
from models.shipyard import Shipyard

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
    back_choice_name:str

    def __init__(self, name:str, choice_type:ChoiceType):
        self.name = name
        self.choice_type = choice_type
        self.text = ""
        self.route = ""
        self.next_choice_name = ""
        self.options = []
        self.back_choice_name = ""

    def is_root(self) -> bool:
        return self.name == "root"

class Menu:
    """ Menu Handler """
    def __init__(self, hero:Hero) -> None:
        self.hero = hero
        self.debug = self.hero.debug
        self.printer:Printer = Printer(self.hero.debug)
        self.choice_by_name:dict[str,Choice] = {}
        self.default_quit_choice = Choice("quit", ChoiceType.ACTION)
        self.current_choice:Choice = self.default_quit_choice
        self.current_ship:Ship|None = None
        self.headquarter_shipyard_waypoints:list[Waypoint] = []
        self.current_headquarter_waypoint:Waypoint|None = None
        self.current_ship_type:str = ""
        self.current_system:System = ""

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
                    choice.back_choice_name = obj.get("back", "")
                    self.choice_by_name[choice.name] = choice
                # root and quit are a required node
                # action needs route
                self.current_choice = self.choice_by_name["root"]
            except yaml.YAMLError as exc:
                print(exc)
                print(f"Unable to read from file named {filename}")

    def ask(self, question:str) -> str:
        return prompt([IText("answer", message=question)])["answer"]

    def ask_with_choice(self, question:str, choices:list[str], variable_name:str="answer") -> str:
        """ Ask user for a choice """
        questions:list[IList] = [
          IList(variable_name, message=question, choices=choices)
        ]
        answers = prompt(questions)
        if answers is None:
            return ""
        return answers[variable_name]

    def advance_current_choice(self, the_next_name:str|None=None) -> bool:
        """ True: keep going, False: stop """
        if the_next_name is None:
            the_next_name = self.current_choice.next_choice_name
        if the_next_name == "quit":
            return False
        self.current_choice:Choice = self.choice_by_name.get(the_next_name, self.default_quit_choice)
        return self.current_choice.name != "quit"

    def back_current_choice(self) -> None:
        if self.current_choice is None:
            return
        back:str = self.current_choice.back_choice_name
        self.current_choice:Choice = self.choice_by_name.get(back, self.default_quit_choice)

    def add_back(self, choices:list[str]) -> str:
        cancel_text:str = "back"
        choices.insert(0, cancel_text)
        return cancel_text

    def query_user(self) -> bool:
        """ True to keep going, False to quit """
        if self.current_choice is not None:
            if self.debug:
                print(self.current_choice)
            match self.current_choice.choice_type:
                case ChoiceType.PROMPT:
                    choice:str = self.ask_with_choice(
                            self.current_choice.text,
                            list(map(lambda x: x.text, self.current_choice.options)))
                    matching_option:Option = Option("", "root")
                    for option in self.current_choice.options:
                        if option.text == choice:
                            matching_option = option
                            break
                    return self.advance_current_choice(matching_option.next_choice_name)
                case ChoiceType.ACTION:
                    print(f"Action {self.current_choice.route}")
                    match self.current_choice.route:
                        case "quit":
                            return False
                        case "get_agent":
                            self.printer.print_agent(self.hero.get_agent())
                        case "get_systems":
                            self.printer.print_systems(self.hero.get_systems())
                        case "get_headquarter":
                            hq:Waypoint = self.hero.get_headquarter()
                            self.printer.print_waypoint(hq)
                        case "get_headquarter_waypoints":
                            self.printer.print_waypoints(self.hero.get_headquarter_waypoints())
                        case "get_headquarter_shipyard_waypoint":
                            waypoint_names:list[str] = list(map(lambda s: s.waypoint, self.headquarter_shipyard_waypoints))
                            cancel_text:str = self.add_back(waypoint_names)
                            waypoint:str = self.ask_with_choice("Choose a waypoint?", waypoint_names)
                            if waypoint == cancel_text:
                                self.back_current_choice()
                                return True

                            matching:Waypoint|None = next((s for s in self.headquarter_shipyard_waypoints if s.waypoint == waypoint), None)
                            if matching is None:
                                print("Unable to find matching waypoint.")
                            else:
                                self.current_headquarter_waypoint = matching
                                print(matching)
                        case "get_headquarter_ships":
                            shipyard:Shipyard = self.hero.get_shipyard(self.current_headquarter_waypoint.waypoint)
                            ship_types:list[str] = shipyard.ship_types
                            cancel_text:str = self.add_back(ship_types)
                            ship_type:str = self.ask_with_choice("Buy a ship?", ship_types)
                            if ship_type == cancel_text:
                                self.back_current_choice()
                                return True
                            self.current_ship_type = ship_type
                        case "update_headquarter_ships":
                            resp = self.hero.buy_ship(self.current_ship_type, self.current_headquarter_waypoint.waypoint)
                            if self.debug:
                                print(resp)
                        case "get_headquarter_shipyard_waypoints":
                            self.headquarter_shipyard_waypoints:list[Waypoint] = self.hero.get_headquarter_shipyard_waypoints()
                            self.printer.print_waypoints(self.headquarter_shipyard_waypoints)
                        case "get_my_ships":
                            self.hero.get_my_ships()
                            ships:list[Ship] = list(self.hero.ships_by_symbol.values())
                            self.printer.print_ships(ships)
                        case "get_ship":
                            ships:list[Ship] = list(self.hero.ships_by_symbol.values())
                            names:list[str] = [ship.name for ship in ships]
                            cancel_text:str = self.add_back(names)
                            ship_name:str = self.ask_with_choice("Which ship do you want to view?", names)
                            if ship_name == cancel_text:
                                self.back_current_choice()
                                return True

                            ship:Ship = self.hero.ships_by_symbol[ship_name]
                            self.current_ship = ship
                        case "update_ship":
                            actions:list[str] = ["Info", "Move", "Orbit", "Dock", "Refuel", "Extract"]
                            # fail the app immediately if ship isn't set here
                            #   as it should be
                            if self.current_ship is None:
                                return False
                            cancel_text:str = self.add_back(actions)
                            print(self.current_ship.is_docked())
                            match self.ask_with_choice("Actions?", actions):
                                case x if x == cancel_text:
                                    self.back_current_choice()
                                    return True
                                case "Info":
                                    self.printer.print_ship(self.current_ship)
                                case "Move":
                                    answer:str = self.ask("Where to (waypoint symbol)?")
                                    nav:ShipNav = self.current_ship.fly(answer.upper())
                                    if self.debug:
                                        print(nav)
                                case "Orbit":
                                    resp = self.current_ship.orbit()
                                    if self.debug:
                                        print(resp)
                                case "Dock":
                                    nav:ShipNav = self.current_ship.dock()
                                    if self.debug:
                                        print(nav)
                                case "Refuel":
                                    resp = self.current_ship.refuel()
                                    if self.debug:
                                        print(resp)
                                case "Extract":
                                    resp = self.current_ship.mine()
                                    if self.debug:
                                        print(resp)
                        case "get_contracts":
                            contracts = self.hero.get_contracts()
                            contract_ids = list(map(lambda c: c.id, contracts))
                            if len(contracts) == 0:
                                print("No contracts")
                            else:
                                self.printer.print_list({"Contract IDs": contract_ids})
                        case "get_contract":
                            contract_ids = list(map(lambda c: c.id, self.hero.get_contracts()))
                            cancel_text:str = self.add_back(contract_ids)
                            contract_id:str = self.ask_with_choice("Which contract do you want to view?", contract_ids)
                            if contract_id == cancel_text:
                                self.back_current_choice()
                                return True
                            contract:Contract|None = self.hero.get_contract_by_id(contract_id)
                            if contract is None:
                                print("Contract not found")
                            else:
                                self.printer.print_contract(contract)
                                if not contract.accepted:
                                    match self.ask_with_choice("Do you want to accept contract?", ["yes", "no"]):
                                        case "yes":
                                            self.hero.accept_contract(contract_id)
                                            print("Accepted!")
                        case "update_contract":
                            actions:list[str] = ["Accept"]
                            cancel_text:str = self.add_back(actions)
                            action:str = self.ask_with_choice("Actions?", actions)
                            if action == cancel_text:
                                self.back_current_choice()
                                return True
                            print(action)
                        case "get_system":
                            system_names:list[str] = list(map(lambda s: s.name, self.hero.systems))
                            cancel_text:str = self.add_back(system_names)
                            system_name:str = self.ask_with_choice("Pick a system to learn more", system_names)
                            if system_name == cancel_text:
                                self.back_current_choice()
                                return True
                            matching:System|None = next((s for s in self.hero.systems if s.name == system_name), None)
                            if matching is None:
                                return False
                            self.current_system = self.hero.get_system(matching.symbol)
                            self.printer.print_system(self.current_system)
                        case "system_actions":
                            actions:list[str] = ["Info", "Waypoints"]
                            cancel_text:str = self.add_back(actions)
                            system_symbol:str = self.current_system.symbol
                            match self.ask_with_choice("Actions?", actions):
                                case x if x == cancel_text:
                                    self.back_current_choice()
                                    return True
                                case "Info":
                                    system:System = self.hero.get_system(system_symbol)
                                    self.printer.print_system(system)
                                case "Waypoints":
                                    self.printer.print_waypoints(self.hero.get_waypoints(system_symbol))

                    return self.advance_current_choice()
        return False

