from pydantic import BaseModel
from typing import Optional

from zone import Zone


class Drone(BaseModel):
    """
    Represents one drone during simulation.
    """
    def __init__(self,
                 drone_id: int,
                 current_zone: Zone,
                 finish: bool = False,
                 in_transit_to: Optional[str] = None,
                 turns_to_arrival: int = 0
                 ):
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.finish = finish
        self.in_transit_to = in_transit_to
        self.turns_to_arrival = turns_to_arrival

    def start_transit(self, destination: str, cost: int) -> None:
        """
        Mark the drone as moving toward destination for `cost` turns.
        """
        self.in_transit_to = destination
        self.turns_to_arrival = cost

    def tick(self) -> None:
        """
        Advance one simulation turn and complete movement when needed.
        """
        if self.turns_to_arrival > 0:
            self.turns_to_arrival -= 1
        if self.turns_to_arrival == 0 and self.in_transit_to is not None:
            self.current_zone = self.in_transit_to
            self.in_transit_to = None
