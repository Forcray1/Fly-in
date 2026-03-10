from dataclasses import dataclass


class ZoneType(str):
    """Supported zone types."""

    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


@dataclass(slots=True)
class Zone:
    """
    A graph zone with optional metadata.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: str = "none"
    max_drones: int = 1

