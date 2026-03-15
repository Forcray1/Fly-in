from pydantic import BaseModel


class ZoneType(str):
    """
    Supported zone types.
    """

    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class Zone(BaseModel):
    """
    A graph zone with optional metadata.

    Zones represent locations in the map. Connections between zones
    are managed by the Graph class, not stored here.
    """
    name: str
    x: int
    y: int
    zone_type: str = ZoneType.NORMAL
    color: str = "none"
    max_drones: int = 1
    current_drones: list = []

    @classmethod
    def from_cords(
        cls,
        name: str,
        cords: tuple,
        zone_type: str = ZoneType.NORMAL,
        color: str = "none",
        max_drones: int = 1
    ):
        return cls(
            name=name,
            x=cords[0],
            y=cords[1],
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            current_drones=[]
        )

    def is_passable(self) -> bool:
        """
        Check if the zone is passable (not blocked).
        """
        return self.zone_type != ZoneType.BLOCKED

    def is_blocked(self) -> bool:
        """
        Check if the zone is blocked.
        """
        return self.zone_type == ZoneType.BLOCKED

    def is_restricted(self) -> bool:
        """
        Check if the zone has restrictions.
        """
        return self.zone_type == ZoneType.RESTRICTED

    def is_priority(self) -> bool:
        """
        Check if the zone is a priority zone.
        """
        return self.zone_type == ZoneType.PRIORITY

    def has_capacity(self) -> bool:
        """
        Check if there is available capacity for another drone.
        """
        return len(self.current_drones) < self.max_drones

    def get_available_capacity(self) -> int:
        """
        Get the number of available drone slots.
        """
        return max(0, self.max_drones - len(self.current_drones))

    def add_drone(self, drone) -> bool:
        """
        Add a drone to this zone.
        """
        from .drone import Drone
        if not isinstance(drone, Drone):
            raise TypeError("drone must be a Drone instance")
        if self.has_capacity():
            self.current_drones.append(drone)
            return True
        return False

    def remove_drone(self, drone_id: int) -> bool:
        """
        Remove a drone from this zone by id.
        """
        for drone in self.current_drones:
            if getattr(drone, 'drone_id', None) == drone_id:
                self.current_drones.remove(drone)
                return True
        return False

    def get_drone_count(self) -> int:
        """
        Get the number of drones currently in this zone.
        """
        return len(self.current_drones)

    def get_position(self) -> tuple:
        """
        Get the coordinates of this zone.
        """
        return (self.x, self.y)

    def get_zone_type(self) -> str:
        """
        Get the zone type.
        """
        return self.zone_type

    def get_metadata(self) -> dict:
        """
        Get all zone metadata.
        """
        return {
            "name": self.name,
            "position": self.get_position(),
            "zone_type": self.zone_type,
            "color": self.color,
            "max_drones": self.max_drones,
            "current_drones": self.current_drones,
            "available_capacity": self.get_available_capacity()
        }

    def validate(self) -> bool:
        """
        Validate that the zone has valid properties.
        """
        return (
            isinstance(self.name, str)
            and len(self.name) > 0
            and isinstance(self.x, int)
            and isinstance(self.y, int)
            and self.max_drones > 0
            and isinstance(self.current_drones, list)
            and 0 <= len(self.current_drones) <= self.max_drones
            and self.zone_type in [
                ZoneType.NORMAL,
                ZoneType.RESTRICTED,
                ZoneType.PRIORITY,
                ZoneType.BLOCKED,
            ]
        )

    def reset(self) -> None:
        """
        Reset the zone to its initial state.
        """
        self.current_drones = []
        self.cost_to_next = 0
        self.cost_to_end = 0

    def __repr__(self) -> str:
        """
        String representation of the zone.
        """
        return (
            f"Zone(name={self.name}, pos=({self.x}, {self.y}), "
            f"type={self.zone_type}, "
            f"drones={len(self.current_drones)}/{self.max_drones})"
        )
