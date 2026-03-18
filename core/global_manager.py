from copy import deepcopy
from typing import Dict, List, Tuple, Any
from classes.graph import Graph
from core.A_star import a_star


class SimulationManager:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.paths_cache: Dict[int, List[str]] = {}
        self.global_occ: Dict[str, int] = {
            name: 0 for name in graph.zones
        }
        self.turns = 0

    def run_simulation(self) -> Tuple[int, List[Any]]:
        """
        Run the simulation and return (number_of_turns, list_of_steps).
        """
        steps: List[Any] = []

        start_hub = self.graph.start_hub
        end_hub = self.graph.end_hub
        if start_hub is None or end_hub is None:
            return self.turns, steps

        steps.append(deepcopy(self.graph.drones))

        while not (
                   all(d.finish for d in self.graph.drones)
                   and self.turns < 2000
                   ):
            self.turns += 1
            turn_movements: List[str] = []
            res_zones: Dict[str, int] = {}
            res_links: Dict[Tuple[str, str], int] = {}

            # Arrival of drones in transit (Restricted management)
            for drone in self.graph.drones:
                if not drone.finish and drone.turns_to_arrival > 0:
                    drone.turns_to_arrival -= 1
                    if drone.turns_to_arrival == 0:
                        dest_name = drone.in_transit_to
                        if dest_name is not None:
                            dest_zone = self.graph.get_zone(dest_name)
                            drone.current_zone = dest_zone
                            dest_zone.add_drone(drone)
                            turn_movements.append(
                                f"D{drone.drone_id}-{dest_name}"
                            )
                            if dest_name == end_hub.name:
                                drone.finish = True
                        drone.in_transit_to = None

            # Planning and Movement
            active_drones = [
                d for d in self.graph.drones
                if not d.finish and d.turns_to_arrival == 0
            ]
            # Sort to smooth traffic
            active_drones.sort(key=lambda d: len(
                a_star(
                    self.graph, d.current_zone,
                    end_hub, self.global_occ
                ) or []
            ))

            for drone in active_drones:
                path = a_star(
                    self.graph, drone.current_zone,
                    end_hub, self.global_occ
                )
                if not path or len(path) < 2:
                    continue

                next_name = path[1]
                next_zone = self.graph.get_zone(next_name)

                sorted_link = sorted([drone.current_zone.name, next_name])
                link_key: Tuple[str, str] = (sorted_link[0], sorted_link[1])

                # Capacity check
                conn_cap = self.graph.connections_data.get(link_key, 1)
                if res_links.get(link_key, 0) >= conn_cap:
                    continue

                if next_name != end_hub.name:
                    count_in_zone = next_zone.get_drone_count()
                    res_in_zone = res_zones.get(next_name, 0)
                    if (count_in_zone + res_in_zone) >= next_zone.max_drones:
                        continue

                # Execute movement
                drone.current_zone.remove_drone(drone.drone_id)
                res_links[link_key] = res_links.get(link_key, 0) + 1
                res_zones[next_name] = res_zones.get(next_name, 0) + 1
                self.global_occ[next_name] += 1

                if next_zone.zone_type == "restricted":
                    drone.start_transit(next_name, 1)
                    turn_movements.append(f"D{drone.drone_id}-{next_name}")
                else:
                    drone.current_zone = next_zone
                    next_zone.add_drone(drone)
                    turn_movements.append(f"D{drone.drone_id}-{next_name}")
                    if next_name == end_hub.name:
                        drone.finish = True

            if turn_movements:
                print(" ".join(turn_movements))

            steps.append(deepcopy(self.graph.drones))

        return self.turns, steps


def global_manager(graph: Graph) -> Tuple[int, List[Any]]:
    """
    Bridge function for main
    """
    manager = SimulationManager(graph)
    return manager.run_simulation()
