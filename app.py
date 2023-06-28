import sys
from models import Hero

def main() -> int:
    """ Main function """
    hero = Hero()
    hero.init_from_file("data.yaml")

    # get agent info
    hero.get_agent()
    return 0

if __name__ == '__main__':
    sys.exit(main())
