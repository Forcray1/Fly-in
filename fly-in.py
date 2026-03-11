import sys

from parser.parser_map import parser


def main():
    config = sys.argv[1]
    infos = parser(config)
    for item, value in infos.items():
        print(item)
        print(value)


if __name__ == "__main__":
    main()
