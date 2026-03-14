import sys

from parser.parser_map import parser
from parser.check_value import check_value
from classes.connexion import Connexion
#  from classes.drone import Drone
from classes.zone import Zone
from classes.graph import Graph
from core.A_star import a_star


def main():
    """
    Core logic of the project
    """
    graph = Graph()
    config = sys.argv[1]
    try:
        infos = parser(config)
        if not check_value(infos):
            return
        print("Infos from parser:\n")
        for item, value in infos.items():
            if item not in ("connection", "hub"):
                print(item)
                print(value)
                print("\n")
    except Exception as e:
        print(f"ERROR: {e}")

    for hub in [infos["start_hub"], infos["end_hub"]] + infos["hubs"]:
        if hub is not None:
            zone = Zone.from_cords(
                name=hub["name"],
                cords=(hub["x"], hub["y"]),
                zone_type=hub.get("zone", "normal"),
                color=hub.get("color", "none"),
                max_drones=hub.get("max_drones", 1),
            )
            graph.add_zone(zone)

    for connection in infos["connections"]:
        co = Connexion.create(
            connection["from"],
            connection["to"],
            connection["max_link_capacity"]
        )
        graph.add_connection(co)
    print("\nGraph infos\n")
    print(graph.zones)
    print("\n")
    print(graph.adjacency)
    print("\n")
    print(graph.link_capacity)

    start = infos["start_hub"]["name"]
    goal = infos["end_hub"]["name"]
    path = a_star(graph, start, goal)
    print(f"\nChemin A* de {start} à {goal} : {path}")


if __name__ == "__main__":
    main()
