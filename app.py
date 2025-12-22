from models import Hero, Menu
from pyfiglet import Figlet

def print_ascii_text(figlet:Figlet, text:str) -> None:
    """ Print ascii text """
    print(figlet.renderText(text))

def main() -> None:
    """ Main function """
    hero:Hero = Hero()
    hero.init_from_file("data.yaml")

    f:Figlet = Figlet()
    print_ascii_text(f, f"Welcome {hero.callsign}")

    menu:Menu = Menu(hero)
    menu.init_from_file("menu.yaml")

    try:
        keep_going:bool = True
        while keep_going:
            keep_going = menu.query_user()
    except KeyboardInterrupt:
        print("Thank You!")

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

if __name__ == '__main__':
    main()
