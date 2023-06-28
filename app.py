import sys
from models import Hero

def main() -> int:
    """ Main function """
    hero = Hero()
    hero.init_from_file("data.yaml")

if __name__ == '__main__':
    sys.exit(main())
