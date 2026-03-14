from collections import defaultdict
from typing import Dict, Set, Tuple

from classes.connexion import Connexion
from classes.zone import Zone


class Graph:
    """
    Stores zones and bidirectional connections with capacities.
    """

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.link_capacity: Dict[Tuple[str, str], int] = {}

    def add_zone(self, zone) -> None:
        """
        Register a new zone by name.
        """
        # Delayed import to avoid circular dependency
        from classes.zone import Zone
        if not isinstance(zone, Zone):
            raise TypeError("zone must be a Zone instance")
        self.zones[zone.name] = zone

    def add_connection(self,
                       connexion: Connexion
                       ) -> None:
        """
        Add a bidirectional connection between two known zones.
        """
        if (connexion.zone_a not in self.zones or
                connexion.zone_b not in self.zones):
            raise ValueError("Connection references an unknown zone")
        self.adjacency[connexion.zone_a].add(connexion.zone_b)
        self.adjacency[connexion.zone_b].add(connexion.zone_a)
        self.link_capacity[(connexion.zone_a,
                            connexion.zone_b)] = connexion.max_link_capacity

    def neighbors(self, zone_name: str) -> Set[str]:
        """
        Return connected neighbors for one zone.
        """
        return self.adjacency.get(zone_name, set())

    def get_zone(self, zone_name: str) -> Zone:
        """
        Return zone by name.
        """
        return self.zones[zone_name]
