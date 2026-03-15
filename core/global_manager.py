from classes.graph import Graph
from classes.drone import Drone
from classes.zone import Zone
from core.A_star import a_star


def move_drone_cache(drone: Drone,
                     graph: Graph,
                     reservations: set,
                     paths_cache: dict
                     ):
    """
    Version optimisée avec cache de chemin.
    """
    if drone.finish:
        return
    path = paths_cache.get(drone.drone_id)
    if not path or drone.current_zone.name != path[0]:
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


def move_drone_base(drone: Drone, graph: Graph, reservations: set):
    """
    Version de base : recalcule A* à chaque tour.
    """
    if drone.finish:
        return
    path = a_star(graph, drone.current_zone, graph.end_hub)
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


def priority(drones: list[Drone], graph: Graph, goal: Zone) -> Drone:
    """
    Return the drone with the less amount of moves to goal
    """
    candidates = [d for d in drones if not d.finish]
    best_drone = min(
        candidates,
        key=lambda d: len(a_star(graph,
                                 d.current_zone,
                                 goal)) if a_star(graph,
                                                  d.current_zone,
                                                  goal) else float('inf')
    )
    return best_drone


def finished(drones: list[Drone]) -> bool:
    """
    Check if each drone is to the goal
    """
    for drone in drones:
        if not drone.finish:
            return False
    return True


def global_manager(graph: Graph) -> int:
    """
    Choisit dynamiquement la meilleure stratégie selon la taille
    du graphe et du nombre de drones.
    """
    nb_zones = len(graph.zones)
    nb_drones = len(graph.drones)
    PETIT_GRAPHE = nb_zones < 30 and nb_drones < 10
    turns = 0
    if PETIT_GRAPHE:
        paths_cache = {drone.drone_id: None for drone in graph.drones}
        while not finished(graph.drones):
            turns += 1
            moved = False
            reservations = set()
            for drone in graph.drones:
                if drone.finish:
                    continue
                before_zone = drone.current_zone
                move_drone_cache(drone, graph, reservations, paths_cache)
                if drone.current_zone != before_zone:
                    moved = True
            if not moved:
                break
    else:
        while not finished(graph.drones):
            turns += 1
            moved = False
            reservations = set()
            for drone in graph.drones:
                if drone.finish:
                    continue
                before_zone = drone.current_zone
                move_drone_base(drone, graph, reservations)
                if drone.current_zone != before_zone:
                    moved = True
            if not moved:
                break
    return turns
