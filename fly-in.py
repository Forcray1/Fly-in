import sys

from parser.parser_map import parser
from parser.check_value import check_value
from classes.connexion import Connexion
from classes.drone import Drone
from classes.zone import Zone
from classes.graph import Graph
from core.A_star import a_star

from core.global_manager import global_manager
from visualisation.visualisation import visualise


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
            if item not in ("hub"):
                print(item)
                print(value)
                print("\n")

        for hub in [infos["start_hub"], infos["end_hub"]] + infos["hubs"]:
            zone = Zone.from_cords(
                name=hub["name"],
                cords=(hub["x"], hub["y"]),
                zone_type=hub.get("zone", "normal"),
                color=hub.get("color", "none"),
                max_drones=hub.get("max_drones", 1),
            )
            graph.add_zone(zone)
            if hub == infos["start_hub"]:
                graph.start_hub = zone
            if hub == infos["end_hub"]:
                graph.end_hub = zone

        for connection in infos["connections"]:
            co = Connexion.create(
                connection["from_"],
                connection["to"],
                max_link_capacity=connection["max_link_capacity"]
            )
            graph.add_connection(co)
        print("\nGraph infos\n")
        print(graph.zones)
        print("\n")
        print(graph.adjacency)
        print("\n")
        print(graph.zones_capacity)

        assert graph.start_hub is not None, "start_hub should not be None"
        assert graph.end_hub is not None, "end_hub should not be None"
        start = graph.start_hub
        goal = graph.end_hub
        path = a_star(graph, start, goal)
        print(f"\nChemin A* de {start.name} à {goal.name} : {path}")

        i = int(infos["nb_drones"])
        d_id = 0
        while d_id < i:
            d_id += 1
            drone = Drone(drone_id=d_id, current_zone=graph.start_hub)
            graph.drones.append(drone)
            graph.start_hub.current_drones.append(drone)
        print(f"\ncreated drones supposed {infos["nb_drones"]}:")
        for drone in graph.drones:
            print(drone)
        from copy import deepcopy
        graph2 = deepcopy(graph)
        turns, steps = global_manager(graph2)
        if all(drone.finish for drone in graph2.drones):
            print(f"All the drones made it to the goal in {turns} moves !!")
        else:
            print("Certains drones n'ont pas atteint le goal.")
        visualise(graph2, steps)
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
