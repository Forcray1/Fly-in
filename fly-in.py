import sys

from parser.parser_map import parser
from parser.check_value import check_value  # type: ignore


def main():
    config = sys.argv[1]
    try:
        infos = parser(config)
        if not check_value(infos):
            return
        for item, value in infos.items():
            if item not in ("connections", "hubs"):
                print(item)
                print(value)
                print("\n")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
