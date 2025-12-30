from models import Hero, Menu
from pyfiglet import Figlet
from time import sleep
from argparse import ArgumentParser

def print_ascii_text(figlet:Figlet, text:str) -> None:
    """ Print ascii text """
    print(figlet.renderText(text))

def main(ship:str, mine:str, market:str, contract:str, contract_id:str, ore:str) -> None:
    """ Main function, with symbols """
    hero:Hero = Hero()
    hero.init_from_file("data.yaml")

    f:Figlet = Figlet()
    print_ascii_text(f, f"Autominer")

    print(f"ship: {ship}, mine: {mine}, market: {market}, contract: {contract}, ore: {ore}, contract_id: {contract_id}")

    # get info
    # hero.get_agent()
    # hero.get_headquarter_waypoints()
    # hero.get_my_ships()
    # hero.get_contracts()

    # do things
    # hero.accept_all_contracts()
    # hero.buy_ship(ship_type, nav_symbol)
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
    # hero.get_market(ship_name)

if __name__ == '__main__':
    parser = ArgumentParser(
                    prog='Autominer',
                    description='Automatically mines',
                    epilog='')
    # parser.add_argument("-s", "--ship", type=str, default=25, help="User age (default: 25)")
    parser.add_argument("-s", "--ship", type=str, help="Ship symbol")
    parser.add_argument("-i", "--mine", type=str, help="Mine symbol")
    parser.add_argument("-a", "--market", type=str, help="Market symbol")
    parser.add_argument("-c", "--contract", type=str, help="Contract symbol")
    parser.add_argument("-d", "--contract-id", type=str, help="Contract id")
    parser.add_argument("-o", "--ore", type=str, help="Ore to fulfill contract")
    args = parser.parse_args()
    main(args.ship, args.mine, args.market, args.contract, args.contract_id, args.ore)
