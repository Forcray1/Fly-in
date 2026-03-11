from collections import defaultdict
from typing import Dict, Set, Tuple

from .zone import Zone


class Graph:
    """
    Stores zones and bidirectional connections with capacities.
    """

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.link_capacity: Dict[Tuple[str, str], int] = {}

    def add_zone(self, zone: Zone) -> None:
        """
        Register a new zone by name.
        """
        self.zones[zone.name] = zone

    def add_connection(self,
                       zone_a: str,
                       zone_b: str,
                       capacity: int = 1
                       ) -> None:
        """
        Add a bidirectional connection between two known zones.
        """
        if zone_a not in self.zones or zone_b not in self.zones:
            raise ValueError("Connection references an unknown zone")
        self.adjacency[zone_a].add(zone_b)
        self.adjacency[zone_b].add(zone_a)
        self.link_capacity[(zone_a, zone_b)] = capacity
        self.link_capacity[(zone_b, zone_a)] = capacity

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
