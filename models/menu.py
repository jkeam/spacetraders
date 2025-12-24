import yaml
from collections import deque
from dataclasses import dataclass
from enum import Enum
from inquirer import prompt, List as IList
from models.hero import Hero
from models.agent import Agent
from models.system import System
from models.waypoint import Waypoint
from models.ship import Ship
from models.contract import Contract
from models.printer import Printer

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
        self.printer:Printer = Printer(self.hero.debug)

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

    def advance_current_choice(self, the_next_name:str|None=None) -> bool:
        """ True: keep going, False: stop """
        if the_next_name is None:
            the_next_name = self.current_choice.next_choice_name
        if the_next_name == "quit":
            return False
        self.current_choice = self.choice_by_name.get(the_next_name, "quit")
        return self.current_choice != "quit"

    def back_current_choice(self) -> None:
        if self.current_choice is None:
            return
        self.current_choice = self.choices.pop()
        # keep popping until we get a prompt type
        while self.current_choice.choice_type != ChoiceType.PROMPT:
            self.current_choice = self.choices.pop()

    def reset_choices(self) -> None:
        self.choices.clear()

    def add_back(self, choices) -> str:
        cancel_text:str = "back"
        choices.insert(0, cancel_text)
        return cancel_text

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
                    return self.advance_current_choice(matching.next_choice_name)
                case ChoiceType.ACTION:
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
                        case "get_ships":
                            self.hero.get_my_ships()
                            ships:list[Ship] = self.hero.ships_by_symbol.values()
                            self.printer.print_ships(ships)
                            names:list[str] = [ship.name for ship in ships]
                        case "get_ship":
                            ships:list[Ship] = self.hero.ships_by_symbol.values()
                            names:list[str] = [ship.name for ship in ships]
                            cancel_text:str = self.add_back(names)
                            ship_name:str = self.ask_with_choice("Which ship do you want to view?", names)
                            if ship_name == cancel_text:
                                self.back_current_choice()
                                return True

                            ship:Ship = self.hero.ships_by_symbol[ship_name]
                            self.printer.print_ship(ship)
                        case "get_contracts":
                            contracts = self.hero.get_contracts()
                            contract_ids = list(map(lambda c: c.id, contracts))
                            if len(contracts) == 0:
                                print("No contracts")
                            else:
                                self.printer.print_list({"Contract IDs": contract_ids})
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
                        case "get_waypoints":
                            system_names:list[str] = list(map(lambda s: s.name, self.hero.systems))
                            cancel_text:str = self.add_back(system_names)
                            system:str = self.ask_with_choice("Want waypoints?", system_names)
                            if system == cancel_text:
                                self.back_current_choice()
                                return True

                            matching:System|None = next((s for s in self.hero.systems if s.name == system), None)
                            if matching is None:
                                print("Unable to find matching system.")
                            else:
                                self.printer.print_waypoints(self.hero.get_waypoints(matching.symbol))

                    return self.advance_current_choice()
        return False

