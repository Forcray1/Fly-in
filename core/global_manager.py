
from classes.graph import Graph
from classes.drone import Drone
from classes.zone import Zone
from core.A_star import a_star


def move_drone_cache(drone: Drone,
                     graph: Graph,
                     reservations: dict,
                     paths_cache: dict
                     ):
    """
    optimised version for smaller ones, wich keep the cache of A*
    """
    if drone.finish:
        return
    path = paths_cache.get(drone.drone_id)
    if not path or drone.current_zone.name != path[0]:
        assert graph.end_hub is not None, "end_hub should not be None"
        if isinstance(drone.current_zone, Zone):
            path = a_star(graph, drone.current_zone, graph.end_hub)
        else:
            path = None
        paths_cache[drone.drone_id] = path
    if path and len(path) > 1:
        next_zone_name = path[1]
        if (
            next_zone_name not in reservations
            or reservations.get(next_zone_name) == drone.drone_id
        ):
            if graph.zones[next_zone_name].is_full():
                reservations[next_zone_name] = drone.drone_id
            if (
                isinstance(drone.current_zone, Zone)
                and hasattr(drone.current_zone, "current_drones")
                and drone in drone.current_zone.current_drones
            ):
                drone.current_zone.current_drones.remove(drone)
            drone.current_zone = graph.zones[next_zone_name]
            if (
                next_zone_name in reservations
                and reservations[next_zone_name] == drone.drone_id
            ):
                del reservations[next_zone_name]
            if (
                isinstance(drone.current_zone, Zone)
                and hasattr(drone.current_zone, "current_drones")
            ):
                drone.current_zone.current_drones.append(drone)
            assert graph.end_hub is not None, "end_hub should not be None"
            if next_zone_name == graph.end_hub.name:
                drone.finish = True
                paths_cache[drone.drone_id] = None


def move_drone_base(drone: Drone, graph: Graph, reservations: dict):
    """
    Classic version, wich recalculate A* for each move
    """
    if drone.finish:
        return
    assert graph.end_hub is not None, "end_hub should not be None"
    path = a_star(graph, drone.current_zone, graph.end_hub)
    if path and len(path) > 1:
        next_zone_name = path[1]
        if (
            next_zone_name not in reservations
            or reservations.get(next_zone_name) == drone.drone_id
        ):
            reservations[next_zone_name] = drone.drone_id
            if (
                isinstance(drone.current_zone, Zone)
                and hasattr(drone.current_zone, "current_drones")
                and drone in drone.current_zone.current_drones
            ):
                drone.current_zone.current_drones.remove(drone)
            drone.current_zone = graph.zones[next_zone_name]
            if (
                next_zone_name in reservations
                and reservations[next_zone_name] == drone.drone_id
            ):
                del reservations[next_zone_name]
            drone.current_zone.current_drones.append(drone)
            assert graph.end_hub is not None, "end_hub should not be None"
            if next_zone_name == graph.end_hub.name:
                drone.finish = True


def priority(drones: list[Drone], graph: Graph, goal: Zone) -> list[Drone]:
    """
    Return the sorted list of priority within all of the drones
    """
    def drone_priority_key(drone):
        if drone.finish:
            return (float('inf'), drone.drone_id)
        path = a_star(graph, drone.current_zone, goal)
        return (len(path) if path else float('inf'), drone.drone_id)
    return sorted(drones, key=drone_priority_key)


def finished(drones: list[Drone]) -> bool:
    """
    Check if each drone is to the goal
    """
    for drone in drones:
        if not drone.finish:
            return False
    return True


def global_manager(graph: Graph) -> tuple[int, list]:
    """
    Chose the best strategy based on the graph and number of drones
    """
    nb_zones = len(graph.zones)
    nb_drones = len(graph.drones)
    PETIT_GRAPHE = nb_zones < 30 and nb_drones < 10
    turns = 0
    steps = []

    if PETIT_GRAPHE:
        from copy import deepcopy
        paths_cache = {drone.drone_id: None for drone in graph.drones}
        while not finished(graph.drones):
            turns += 1
            moved = False
            reservations = dict()
            assert graph.end_hub is not None, "end_hub should not be None"
            sorted_drones = priority(graph.drones, graph, graph.end_hub)
            for drone in sorted_drones:
                if drone.finish:
                    continue
                before_zone = drone.current_zone
                move_drone_cache(drone, graph, reservations, paths_cache)
                if drone.current_zone != before_zone:
                    moved = True
            steps.append([deepcopy(d) for d in graph.drones])
            if not moved:
                break
    else:
        from copy import deepcopy
        while not finished(graph.drones):
            turns += 1
            moved = False
            reservations = dict()
            assert graph.end_hub is not None, "end_hub should not be None"
            sorted_drones = priority(graph.drones, graph, graph.end_hub)
            for drone in sorted_drones:
                if drone.finish:
                    continue
                before_zone = drone.current_zone
                move_drone_base(drone, graph, reservations)
                if drone.current_zone != before_zone:
                    moved = True
            steps.append([deepcopy(d) for d in graph.drones])
            if not moved:
                break
    return turns, steps
