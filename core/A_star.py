from typing import List, Dict, Optional, Set
from classes.graph import Graph
from classes.zone import Zone


def heuristic(zone_a: Zone, zone_b: Zone) -> float:
    """
    Manhattan distance between two zones.
    """
    return float(abs(zone_a.x - zone_b.x) + abs(zone_a.y - zone_b.y))


def reconstruct_path(came_from: Dict[str, str], current: str) -> List[str]:
    """
    Reconstruct the path from the came_from dictionary.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def a_star(
    graph: Graph,
    start: Zone,
    goal: Zone,
    global_occ: Dict[str, int]
) -> Optional[List[str]]:
    """
    A* algorithm adapted for Fly-in constraints.
    Takes into account zone costs and global density.
    """
    open_set: Set[str] = {start.name}
    came_from: Dict[str, str] = {}

    g_score = {name: float('inf') for name in graph.zones}
    g_score[start.name] = 0.0

    f_score = {name: float('inf') for name in graph.zones}
    f_score[start.name] = heuristic(start, goal)

    while open_set:
        # Selection of lowest f-node
        current_name = min(open_set, key=lambda n: f_score[n])

        if current_name == goal.name:
            return reconstruct_path(came_from, current_name)

        open_set.remove(current_name)

        for neighbor_name in graph.neighbors(current_name):
            neighbor_zone = graph.get_zone(neighbor_name)

            if neighbor_zone.zone_type == "blocked":
                continue

            # Base cost
            if neighbor_zone.zone_type == "restricted":
                move_cost = 2.0
            elif neighbor_zone.zone_type == "priority":
                move_cost = 0.8
            else:
                move_cost = 1.0

            density_penalty = global_occ.get(neighbor_name, 0) * 0.6

            tentative_g = g_score[current_name] + move_cost + density_penalty

            if tentative_g < g_score[neighbor_name]:
                came_from[neighbor_name] = current_name
                g_score[neighbor_name] = tentative_g
                f_score[neighbor_name] = (
                    tentative_g + heuristic(neighbor_zone, goal)
                )
                open_set.add(neighbor_name)

    return None
