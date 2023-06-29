import sys
from models import Hero

def main() -> int:
    """ Main function """
    hero = Hero()
    hero.init_from_file("data.yaml")

    # prep
    hero.get_agent()
    hero.get_headquarter_waypoints()
    hero.get_my_ships()

    # do things
    # hero.accept_all_contracts()
    # hero.buy_headquarter_mining_drone()

    # see things

    return 0

if __name__ == '__main__':
    sys.exit(main())
