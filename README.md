*This project has been created as part of the 42 curriculum by mlorenzo.*

# Description
Fly-in is a pathfinding and drone management simulation project. The goal is to control a fleet of drones navigating through complex maps with obstacles, bottlenecks, and special zones, optimizing their routes to reach the final destination in the minimum number of turns. The project demonstrates advanced algorithmic strategies and visualizes drone movement in real time.

# Instructions
1. **Requirements:**
	 - Python 3.x
	 - Required packages listed in `requirements.txt`
2. **Installation:**
	 - Clone the repository
	 - Install dependencies: `pip install -r requirements.txt`
3. **Execution:**
	 - Run the main program: `python fly-in.py`
	 - Maps are located in the `maps/` directory. You can select or modify maps for different challenges.

# Resources
- [A* Pathfinding Algorithm - Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/)
- [Python Official Documentation](https://docs.python.org/3/)
- [Graph Theory - GeeksforGeeks](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/)
- **AI Usage:**
	- AI was used for code review about optimisation, only to tell wich way to go for research, and for repetitive task such as type hints
 
# Algorithm Choices & Implementation Strategy

- **Pathfinding:**
	- The core uses the A* algorithm for optimal pathfinding, considering map constraints, bottlenecks, and drone capacities.
	- Drones are managed in a queue system to maximize throughput at bottlenecks and avoid deadlocks.
	- Alternative paths and parallelization are leveraged to minimize total turns.
- **Implementation:**
	- The code is modular, with separate classes for map parsing, drone logic, and visualization.
	- The system anticipates bottlenecks and dynamically adjusts drone priorities.

# Visual Representation Features

...

# Additional Information

- For more details, see the in-code documentation and comments.
