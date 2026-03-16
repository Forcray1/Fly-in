from classes.graph import Graph
from classes.zone import Zone
from typing import List, Dict, Optional


def a_star(graph: Graph, start: Zone, goal: Zone) -> Optional[List[str]]:
    """
    Find the shortest path from start to goal using the A* algorithm.
    Returns a list of zone names representing the path.
    """
    open_set = [(start.name, 0)]
    came_from = {}
    g_score = {zone: float('inf') for zone in graph.zones}
    g_score[start.name] = 0
    f_score = {zone: float('inf') for zone in graph.zones}
    f_score[start.name] = heuristic(start, goal)
    closed_set = set()

    while open_set:
        priority_zones = [(zone_name, score) for (zone_name, score) in open_set
                          if graph.zones[zone_name].zone_type == "priority"]
        if priority_zones:
            current_tuple = min(priority_zones, key=lambda x: f_score[x[0]])
        else:
            current_tuple = min(open_set, key=lambda x: f_score[x[0]])
        current = current_tuple[0]
        open_set = [item for item in open_set if item[0] != current]
        if current == goal.name:
            return reconstruct_path(came_from, current)
        closed_set.add(current)
        for neighbor in get_neighbors(graph, current):
            if neighbor in closed_set:
                continue
            zone_obj = graph.zones[neighbor]
            if zone_obj.zone_type == "blocked":
                continue
            if zone_obj.is_full():
                continue
            if neighbor != goal.name and len(get_neighbors(graph,
                                                           neighbor)) == 1:
                continue
            tentative_g_score = g_score[current] + cost(graph,
                                                        current,
                                                        neighbor)
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(
                    graph.zones[neighbor],
                    goal)
                if neighbor not in [item[0] for item in open_set]:
                    open_set.append((neighbor, f_score[neighbor]))
    return None


def heuristic(zone_a: Zone, zone_b: Zone) -> float:
    """
    theorically the path to goal not taking acount of the roads
    just the distance from point A to point B
    """
    return abs(zone_a.x - zone_b.x) + abs(zone_a.y - zone_b.y)


def reconstruct_path(came_from: Dict[str, str], current: str) -> List[str]:
    """
    Reconstruct the path from the came_from map.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def get_neighbors(graph: Graph, zone_name: str) -> List[str]:
    """
    Return the list of neighbor zone names for a given zone.
    """
    return list(graph.adjacency.get(zone_name, []))


def cost(graph: Graph, from_zone: str, to_zone: str) -> float:
    """
    Return the cost of moving from from_zone to to_zone
    (e.g., based on link capacity, zone type, etc.).
    """
    zone = graph.zones[to_zone]
    if zone.is_full():
        return float('inf')
    base_cost = 1.0
    if zone.zone_type == "restricted":
        base_cost *= 2
    return base_cost
