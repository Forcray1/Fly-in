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
            if hub == infos["start_hub"]:
                graph.start_hub = zone
            if hub == infos["end_hub"]:
                graph.end_hub = zone

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
    steps = []

    def global_manager_with_snapshots(graph):
        turns = 0
        paths_cache = {drone.drone_id: None for drone in graph.drones}
        while not all(drone.finish for drone in graph.drones):
            turns += 1
            moved = False
            reservations = set()
            drones_to_move = [d for d in graph.drones if not d.finish]
            drones_to_move.sort(key=lambda d: -abs(d.current_zone.x - graph.end_hub.x) - abs(d.current_zone.y - graph.end_hub.y))
            for drone in drones_to_move:
                path = paths_cache.get(drone.drone_id)
                if not path or drone.current_zone.name != path[0]:
                    from core.A_star import a_star
                    path = a_star(graph, drone.current_zone, graph.end_hub)
                    paths_cache[drone.drone_id] = path
                if path and len(path) > 1:
                    next_zone_name = path[1]
                    if next_zone_name not in reservations:
                        reservations.add(next_zone_name)
                        if drone in drone.current_zone.current_drones:
                            drone.current_zone.current_drones.remove(drone)
                        drone.current_zone = graph.zones[next_zone_name]
                        drone.current_zone.current_drones.append(drone)
                        if next_zone_name == graph.end_hub.name:
                            drone.finish = True
                        paths_cache[drone.drone_id] = None
                        moved = True
                    else:
                        for d2 in drones_to_move:
                            if d2 != drone and not d2.finish:
                                paths_cache[d2.drone_id] = None
            steps.append([deepcopy(d) for d in graph.drones])
            if not moved:
                break
        return turns

    turns = global_manager_with_snapshots(graph2)
    if all(drone.finish for drone in graph2.drones):
        print(f"All the drones made it to the goal in {turns} moves !!")
    else:
        print("Certains drones n'ont pas atteint le goal.")

    visualise(graph2, steps)


if __name__ == "__main__":
    main()
