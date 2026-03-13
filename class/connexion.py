from pydantic import BaseModel
from typing import Tuple, Optional


class Connexion(BaseModel):
    """
    Bidirectional connection between two zones.
    """

    def __init__(self, zone_a: str, zone_b: str, capacity: Optional[int] = 1):
        self.name = "-".join(zone_a, zone_b)
        self.zone_a: str = zone_a
        self.zone_b: str = zone_b
        self.max_link_capacity: int = capacity

    def __post_init__(self) -> None:
        """
        Validate connection constraints from the subject.
        """
        if not self.zone_a or not self.zone_b:
            raise ValueError("Connection zones must be non-empty")
        if "-" in self.zone_a or "-" in self.zone_b:
            raise ValueError("Zone names in connections cannot contain "
                             "'-' characters")
        if " " in self.zone_a or " " in self.zone_b:
            raise ValueError("Zone names in connections cannot contain spaces")
        if self.max_link_capacity <= 0:
            raise ValueError("max_link_capacity must be a positive integer")

    def key(self) -> Tuple[str, str]:
        """
        Return a canonical key to detect duplicates like a-b and b-a.
        """
        return (min(self.zone_a, self.zone_b), max(self.zone_a, self.zone_b))

    def is_full(self, drones: int) -> bool:
        """
        Check if the connexion is full
        """
        if self.max_link_capacity == drones:
            return True
        else:
            return False
