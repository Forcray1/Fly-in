from pydantic import BaseModel
from typing import Tuple, Optional


class Connexion(BaseModel):
    """
    Bidirectional connection between two zones.
    """
    name: str
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    @classmethod
    def create(cls, zone_a: str, zone_b: str, capacity: Optional[int] = 1):
        name = f"{zone_a}-{zone_b}"
        return cls(
            name=name,
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=capacity
        )

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
