from sys import exit
from models import Hero, Ship
from pyfiglet import Figlet
from inquirer import prompt, List as IList
from tabulate import tabulate

def ask_with_choice(question:str, choices:list[str], variable_name:str="answer") -> str:
    """ Ask user for a choice """
    questions:list[IList] = [
      IList(variable_name, message=question, choices=choices)
    ]
    answers = prompt(questions)
    if answers is None:
        return ""
    return answers[variable_name]

def print_ascii_text(figlet:Figlet, text:str) -> None:
    """ Print ascii text """
    print(figlet.renderText(text))

def print_dict(table: dict[str,str]) -> None:
    new_table:dict[str, list[str]] = {}
    for key, value in table.items():
        new_table[key] = [value]
    print(tabulate(new_table, "keys", tablefmt="simple_grid"))

def print_list(table: dict[str,list[str]]) -> None:
    print(tabulate(table, "keys", tablefmt="simple_grid"))

def main() -> int:
    """ Main function """
    hero:Hero = Hero()
    hero.init_from_file("data.yaml")

    f:Figlet = Figlet()
    print_ascii_text(f, f"Welcome {hero.callsign}")

    match ask_with_choice("What do you want to do?", ["info"]):
        case "info":
            match ask_with_choice("About what?", ["agent", "hq", "ships", "contracts"]):
                case "agent":
                    print_dict(hero.get_agent())
                case "hq":
                    print(hero.get_headquarter_waypoints())
                case "ships":
                    hero.get_my_ships()
                    ship_names: list[str] = hero.ships_by_symbol.keys()
                    print_list({"Ship Names": ship_names})
                    ship_name:str = ask_with_choice("Which ship do you want to view?", ship_names)
                    ship:Ship = hero.ships_by_symbol[ship_name]
                    print(ship)
                case "contracts":
                   contracts = hero.get_contracts()
                   if len(contracts) == 0:
                       print("No contracts")
                case _:
                    print("Invalid choice")
        case _:
            print("Invalid choice")

    # get info
    # hero.get_agent()
    # hero.get_headquarter_waypoints()
    # hero.get_my_ships()
    # hero.get_contracts()

    # do things
    # hero.accept_all_contracts()
    # hero.buy_headquarter_mining_drone()
    # ship_name:str = "SPARKSTER-2"
    # asteroid_field:str = "X1-YU85-76885D"
    # orbital_station:str = "X1-YU85-34607X"

    # need to orbit to fly
    # hero.orbit(ship_name)
    # hero.fly(ship_name, orbital_station)

    # need to dock to refuel
    # hero.dock(ship_name)
    # hero.refuel(ship_name)

    # mine and sell goods
    # ship_names:list[str] = ["SPARKSTER-1", "SPARKSTER-3"]
    # hero.send_ships_to_mine(ship_names)
    # hero.sell_all_cargo_for_ships(ship_names, ["ALUMINUM_ORE"])

    # see things
    # hero.get_cargo(ship_name)
    # hero.view_market(ship_name)

    return 0

if __name__ == '__main__':
    exit(main())
