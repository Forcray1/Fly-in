import sys
from copy import deepcopy
from typing import Dict, Any

from parser.parser_map import parser
from parser.check_value import check_value
from classes.connexion import Connexion
from classes.drone import Drone
from classes.zone import Zone
from classes.graph import Graph
from core.global_manager import global_manager
from visualisation.visualisation import visualise


def main() -> None:
    """
    Core logic of the project - Entry point for the drone simulation.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        return

    graph = Graph()
    config = sys.argv[1]

    try:
        infos: Dict[str, Any] = parser(config)
        if not check_value(infos):
            print("ERROR: Invalid map values.")
            return

        all_hubs = [infos["start_hub"], infos["end_hub"]] + infos["hubs"]
        for hub in all_hubs:
            zone = Zone.from_cords(
                name=hub["name"],
                cords=(hub["x"], hub["y"]),
                zone_type=hub.get("zone", "normal"),
                color=hub.get("color", "none"),
                max_drones=int(hub.get("max_drones", 1)),
            )
            graph.add_zone(zone)
            if hub == infos["start_hub"]:
                graph.start_hub = zone
            if hub == infos["end_hub"]:
                graph.end_hub = zone

        if graph.start_hub is None or graph.end_hub is None:
            print("ERROR: Start or End hub not found in configuration.")
            return

        graph.connections_data = {}
        for connection in infos["connections"]:
            max_cap = int(connection["max_link_capacity"])
            co = Connexion.create(
                connection["from_"],
                connection["to"],
                max_link_capacity=max_cap
            )
            graph.add_connection(co)

            link_key = tuple(sorted([connection["from_"], connection["to"]]))
            graph.connections_data[link_key] = max_cap

        nb_drones = int(infos["nb_drones"])
        for d_id in range(1, nb_drones + 1):
            drone = Drone(drone_id=d_id, current_zone=graph.start_hub)
            graph.drones.append(drone)
            graph.start_hub.current_drones.append(drone)

        graph_sim = deepcopy(graph)
        turns, steps = global_manager(graph_sim)

        if all(drone.finish for drone in graph_sim.drones):
            msg = f"SUCCESS: All drones reached the goal in {turns} turns."
        else:
            msg = f"FAILURE: Simulation ended after "\
                  f"{turns} turns (Incomplete)."
        print(msg)

        visualise(graph, steps)

    except FileNotFoundError:
        print(f"ERROR: File {config} not found.")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
