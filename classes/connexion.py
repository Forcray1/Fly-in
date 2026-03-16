from pydantic import BaseModel
from typing import Tuple


class Connexion(BaseModel):
    """
    Bidirectional connection between two zones.
    """
    name: str
    zone_a: str
    zone_b: str

    @classmethod
    def create(cls, zone_a: str, zone_b: str):
        name = f"{zone_a}-{zone_b}"
        return cls(
            name=name,
            zone_a=zone_a,
            zone_b=zone_b,
        )

    def key(self) -> Tuple[str, str]:
        """
        Return a canonical key to detect duplicates like a-b and b-a.
        """
        return (min(self.zone_a, self.zone_b), max(self.zone_a, self.zone_b))
