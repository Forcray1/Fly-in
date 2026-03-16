from pydantic import BaseModel
from typing import Tuple


class Connexion(BaseModel):
    """
    Bidirectional connection between two zones.
    """
    name: str
    zone_a: str
    zone_b: str
    max_link_capacity: int

    @classmethod
    def create(cls, zone_a: str, zone_b: str, max_link_capacity: int):
        name = f"{zone_a}-{zone_b}"
        return cls(
            name=name,
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity
        )

    def key(self) -> Tuple[str, str]:
        """
        Return a canonical key to detect duplicates like a-b and b-a.
        """
        return (min(self.zone_a, self.zone_b), max(self.zone_a, self.zone_b))

    def is_full(self, nb_drone: int) -> bool:
        return nb_drone >= self.max_link_capacity
