import sys
from models import Hero

def main() -> int:
    """ Main function """
    hero = Hero()
    hero.init_from_file("data.yaml")

    hero.get_agent()
    hero.get_headquarter_waypoints()

    hero.get_contracts()
    # hero.accept_all_contracts()
    hero.get_headquarter_ships()

    return 0

if __name__ == '__main__':
    sys.exit(main())
