*This project has been created as part of the 42 curriculum by mlorenzo.*

# Fly-in: Drone Fleet Management & Pathfinding

## Description
Fly-in is a logistics simulation project focused on optimizing the flow of a drone fleet through a graph-based network. The challenge lies in navigating drones from a **Start Hub** to a **Goal Hub** while strictly adhering to physical and temporal constraints:
* **Zone Capacities:** Each hub has a `max_drones` limit.
* **Link Capacities:** Connections have a `max_link_capacity` (default: 1).
* **Zone Types:** Handling `normal`, `restricted` (2 turns to traverse), `priority` (reduced cost), and `blocked` zones.

The goal is to minimize the total number of turns while avoiding collisions and deadlocks.

## Instructions
1. **Requirements:**
    - Python 3.10+
    - Pygame (for visualization)
2. **Installation:**
    - Clone the repository: `git clone <repository_url>`
    - Install dependencies: `pip install -r requirements.txt`
3. **Execution:**
    - Run the simulation: `python fly-in.py maps/challenger.txt`
    - Use **Space** to pause/resume the visualization.

## Algorithm Choices & Implementation Strategy

### 1. Temporal A* Pathfinding (Time-slot Reservations)
To solve the "Challenger Map" and avoid the "conga line" effect, the algorithm uses a **Time-Aware A***:
- **Cost Calculation:** Instead of static costs, the cost of a zone is determined by its occupancy at the **exact turn** the drone plans to arrive.
- **Congestion Management:** A density penalty is applied to zones nearing saturation, forcing drones to explore alternative "overflow" paths or wait for a window of opportunity.
- **Priority Zones:** The heuristic is weighted to favor `priority` zones, effectively using them as high-speed bypasses.

### 2. Hybrid Simulation Manager
The simulation doesn't just pre-calculate; it adapts:
- **Collision Avoidance:** At each turn, the manager validates physical constraints (link and zone capacities) before authorizing movement.
- **Dynamic Re-routing:** If a drone is blocked by an unexpected bottleneck, the system can recalculate its trajectory in real-time.
- **Throughput Optimization:** Drones are prioritized based on their remaining distance to the goal to maximize network flow.

### 3. Global Algorithm Complexity

- **O(T x D x E log V)$**
- T is the number of turns
- D is the number of drones
- E log V is the performance of the A* Algorithm


## Project Structure
- `classes/`: Core objects (`Graph`, `Zone`, `Drone`, `Connexion`).
- `core/`: High-level logic (`SimulationManager` and `A_star` implementation).
- `parser/`: Map parsing and value validation according to subject specifications.
- `visualisation/`: Real-time Pygame renderer with dynamic scaling.

## Visual Representation Features
- **Dynamic Scaling:** Automatic adjustment of zone sizes and text labels based on graph complexity.
- **Status Colors:** Visual distinction between drone states (In-transit vs. Stabilized) and zone types (Priority, Restricted, etc.).
- **Collision Monitoring:** Overlapping drones are arranged in a circular pattern within hubs to maintain visibility of the total occupancy.

## Resources
- https://www.redblobgames.com/pathfinding/a-star/
- https://en.wikipedia.org/wiki/Network_flow
- https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/
- https://docs.python.org/3/
- https://www.redblobgames.com/pathfinding/a-star/
- https://www.youtube.com/playlist?list=PLzMcBGfZo4-lp3jAExUCewBfMx3UZFkh5

### AI Usage Disclosure
- **Optimization Research:** AI was consulted to brainstorm advanced flow strategies (Time-slots, cost-weighting).
- **Refactoring:** Used for repetitive tasks like adding Type Hints (Mypy compliance) and Flake8 styling, as well as for the color palette of the visualisation.
- **Documentation:** Assistance in structuring this README to match project technicalities.

---

# Additional Information
- **Standard Compliance:** The code follows `flake8` styling and `mypy` strict typing.
- **Performance:** Optimized to solve the Challenger Map well under the 50-turn threshold.