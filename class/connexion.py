from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class Connexion:
    """
    Bidirectional connection between two zones.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Validate connection constraints from the subject."""
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

    def as_display_name(self) -> str:
        """
        Return the connection formatted as <zone1>-<zone2>.
        """
        return f"{self.zone_a}-{self.zone_b}"
