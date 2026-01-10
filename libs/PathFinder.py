import heapq

def heuristic(cell, goal):
    """Manhattan distance heuristic"""
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

def astar_straight_preference(maze, start, goal, turn_penalty=0.001):
    """
    A* pathfinding with preference for straight paths.
    Adds a small penalty for direction changes to favor straighter routes.

    Args:
        maze: Maze object
        start: (x, y) starting position
        goal: (x, y) goal position
        turn_penalty: small penalty (e.g., 0.001) for changing direction
                     Should be much smaller than 1 to not affect optimality

    Returns:
        list of (x, y) cells from start to goal, or None if no path exists
    """
    counter = 0
    # Store (f_score, counter, cell, previous_direction)
    open_set = [(0, counter, start, None)]
    counter += 1

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    # Track the direction we came from for each cell
    direction_from = {start: None}

    open_set_hash = {start}

    while open_set:
        _, _, current, prev_direction = heapq.heappop(open_set)
        open_set_hash.discard(current)

        if current == goal:
            reconstructed_path = reconstruct_path(came_from, current)
            print(f"Path found: {reconstructed_path}")
            print(f"Length: {len(reconstructed_path) - 1} steps")
            return reconstructed_path

        for neighbor in maze.get_neighbors(current):
            # Calculate direction to neighbor
            dx = neighbor[0] - current[0]
            dy = neighbor[1] - current[1]
            current_direction = (dx, dy)

            # Base cost is 1 for moving to neighbor
            move_cost = 1.0

            # Add small penalty if direction changed (turn)
            if prev_direction is not None and current_direction != prev_direction:
                move_cost += turn_penalty

            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                direction_from[neighbor] = current_direction
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)

                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor, current_direction))
                    counter += 1
                    open_set_hash.add(neighbor)

    print("No path exists")
    return None

def reconstruct_path(came_from, current):
    """Reconstruct the path from start to goal"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

direction_map = {
    'forward': (0, 1),
    'back': (0, -1),
    'left': (-1, 0),
    'right': (1, 0)
}

def discover_maze(maze, start, drone):
    """
    Explore maze with drone using DFS to discover all walls.
    Drone physically moves through maze, scanning walls at each position.

    Args:
        maze: Maze object (initially empty)
        start: (x, y) starting position
        drone: Drone object with move_to_block(x, y) and get_barriers() methods

    Returns:
        tuple: (path_taken, cells_explored)
            - path_taken: list of cells drone actually moved through
            - cells_explored: number of unique cells visited
    """

    print("discover_maze()::: Starting maze discovery...")

    def scan_walls(cell):
        """Scan current cell and add walls to maze"""
        x, y = cell
        barriers = drone.get_barriers()

        for direction in barriers:
            dx, dy = direction_map[direction]
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < maze.width and 0 <= neighbor[1] < maze.height:
                maze.add_wall(cell, neighbor)

    def get_unvisited_neighbors(cell, visited):
        """Get passable neighbors that haven't been visited"""
        x, y = cell
        neighbors = []
        for dx, dy in direction_map.values():
            neighbor = (x + dx, y + dy)
            if (0 <= neighbor[0] < maze.width and
                    0 <= neighbor[1] < maze.height and
                    neighbor not in visited and
                    maze.is_passable(cell, neighbor)):
                neighbors.append(neighbor)
        return neighbors

    # DFS exploration
    visited = set()
    stack = [start]
    path = [start]

    # Move drone to start and scan
    drone.move_to_block(start[0], start[1])
    visited.add(start)
    scan_walls(start)

    while stack:
        current = stack[-1]

        # Get unvisited neighbors
        neighbors = get_unvisited_neighbors(current, visited)

        if neighbors:
            # Move to first unvisited neighbor
            next_cell = neighbors[0]
            stack.append(next_cell)

            # Physically move drone
            drone.move_to_block(next_cell[0], next_cell[1])
            path.append(next_cell)

            # Mark as visited and scan
            visited.add(next_cell)
            scan_walls(next_cell)
        else:
            # No unvisited neighbors, backtrack
            stack.pop()
            if stack:
                backtrack_cell = stack[-1]
                drone.move_to_block(backtrack_cell[0], backtrack_cell[1])
                path.append(backtrack_cell)

    print(f"\ndiscover_maze()::: Exploration complete!")
    print(f"discover_maze()::: Cells explored: {len(visited)}")
    print(f"discover_maze()::: Path length (including backtracking): {len(path)}")
    print(f"discover_maze()::: Walls discovered: {len(maze.walls)}")
    print(f"\ndiscover_maze()::: Maze ready for pathfinding!")
    return path, len(visited)

def count_turns(path):
    """Count number of direction changes in a path"""
    if len(path) <= 2:
        return 0

    turns = 0
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        next_cell = path[i + 1]

        dx1 = curr[0] - prev[0]
        dy1 = curr[1] - prev[1]
        dx2 = next_cell[0] - curr[0]
        dy2 = next_cell[1] - curr[1]

        if (dx1, dy1) != (dx2, dy2):
            turns += 1

    return turns

def astar_multi_goal_straight_preference(maze, start, goals):
    """
    A* pathfinding to reach multiple goals (3-4) in optimal order.
    Returns separate path segments for each leg of the journey.

    Args:
        maze: Maze object
        start: (x, y) starting position
        goals: list of 3-4 (x, y) goal positions to visit (in any order)

    Returns:
        list of path segments, where each segment is a list of (x, y) cells
        Example: [
            [(0,0), (1,0), (2,0)],  # start to goal1
            [(2,0), (2,1), (3,1)],  # goal1 to goal2
            [(3,1), (4,1), (4,2)]   # goal2 to goal3
        ]
        Returns None if no valid path exists
    """
    from itertools import permutations

    if not goals:
        return [[start]]

    best_segments = None
    best_length = float('inf')
    best_turns = float('inf')

    # Try all orderings (3! = 6 or 4! = 24 permutations)
    for perm in permutations(goals):
        # Build path: start → goal1 → goal2 → goal3 → (goal4)
        waypoints = [start] + list(perm)

        # Calculate path segments
        segments = []
        total_length = 0
        total_turns = 0
        valid = True

        for i in range(len(waypoints) - 1):
            segment = astar_straight_preference(maze, waypoints[i], waypoints[i + 1])

            if segment is None:
                valid = False
                break

            segments.append(segment)
            total_length += len(segment) - 1
            total_turns += count_turns(segment)

        if valid:
            # Prefer shorter paths, break ties with fewer turns
            if (total_length < best_length or
                    (total_length == best_length and total_turns < best_turns)):
                best_length = total_length
                best_turns = total_turns
                best_segments = segments

    return best_segments
