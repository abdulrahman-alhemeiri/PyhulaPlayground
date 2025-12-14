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

def discover_maze_with_objects_fast(maze, start, drone, object_coordinates, goal):
    """
    Fast exploration: move toward objectives greedily, replan when blocked.
    Uses A* with straight path preference and current knowledge.
    """

    def scan_walls(cell):
        x, y = cell
        barriers = drone.get_barriers()
        for direction in barriers:
            dx, dy = direction_map[direction]
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < maze.width and 0 <= neighbor[1] < maze.height:
                maze.add_wall(cell, neighbor)

    def move_and_scan(target):
        """
        Try to move to target using A* with current knowledge.
        Stops and returns coordinate if we encounter an undetected object on the way.
        Returns: (reached_target: bool, stopped_at_object: tuple or None)
        """
        nonlocal current_pos, path, visited

        route = astar_straight_preference(maze, current_pos, target)

        if not route or len(route) <= 1:
            return False, None

        # Follow the route
        for i, next_cell in enumerate(route[1:], 1):
            # Move physically
            drone.move_to_block(next_cell[0], next_cell[1])
            current_pos = next_cell
            path.append(next_cell)
            visited.add(next_cell)

            # Scan for new walls
            scan_walls(next_cell)

            # Check if we're at an undetected object (not our target)
            if next_cell in objects_remaining and next_cell != target:
                # Found object on the way! Return to handle it
                return False, next_cell

            # Check if newly discovered walls block our planned route
            if i < len(route) - 1:
                next_planned = route[i + 1]
                if not maze.is_passable(next_cell, next_planned):
                    # Blocked! Return to replan
                    return current_pos == target, None

            # If we reached target, return success
            if next_cell == target:
                return True, None

        return current_pos == target, None

    # Initialize
    current_pos = start
    visited = set([start])
    path = [start]
    objects_remaining = set(object_coordinates)

    # Move to start and scan
    drone.move_to_block(start[0], start[1])
    scan_walls(start)

    # Check if start is an object
    if start in objects_remaining:
        drone.perform_360_object_detection()
        objects_remaining.remove(start)
        print(f"Object detected at start {start}. Remaining: {len(objects_remaining)}")

    # Visit all object locations
    while objects_remaining:
        # Find nearest unvisited object
        nearest_obj = min(objects_remaining,
                          key=lambda obj: heuristic(current_pos, obj))

        print(f"Moving toward object at {nearest_obj} (currently at {current_pos})...")

        # Keep trying until we reach it
        while nearest_obj in objects_remaining:
            reached, found_object = move_and_scan(nearest_obj)

            # Check if we found a different object on the way
            if found_object is not None:
                print(f"Found object at {found_object} on the way!")
                drone.perform_360_object_detection()
                objects_remaining.remove(found_object)
                print(f"Object detected at {found_object}. Remaining: {len(objects_remaining)}")
                # Continue toward original target if it still exists
                if nearest_obj not in objects_remaining:
                    break
                continue

            if reached:
                # Reached the target object
                drone.perform_360_object_detection()
                objects_remaining.remove(nearest_obj)
                print(f"Object detected at {nearest_obj}. Remaining: {len(objects_remaining)}")
                break
            else:
                # Blocked, discovered new walls, replan
                print(f"  Path blocked, replanning...")

    # All objects detected, now go to goal
    print(f"All objects detected! Moving to goal at {goal} from {current_pos}...")

    # Check if already at goal
    if current_pos == goal:
        print("Already at goal!")
        drone.land()
        return path, len(visited), False

    # Check if goal was already visited
    if goal in visited:
        print(f"Goal already visited! Taking shortest known path back to {goal}...")

        # Temporarily restrict maze navigation to only visited cells
        def get_visited_neighbors_only(cell):
            """Only return neighbors that we've actually visited"""
            neighbors = []
            x, y = cell
            for dx, dy in direction_map.values():
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)
                if (0 <= nx < maze.width and
                        0 <= ny < maze.height and
                        neighbor in visited and
                        maze.is_passable(cell, neighbor)):
                    neighbors.append(neighbor)
            return neighbors

        # Temporarily replace get_neighbors method
        original_get_neighbors = maze.get_neighbors
        maze.get_neighbors = get_visited_neighbors_only

        # Find shortest path through visited cells only
        route = astar_straight_preference(maze, current_pos, goal)

        # Restore original method
        maze.get_neighbors = original_get_neighbors

        if route and len(route) > 1:
            return route, len(visited), True
        else:
            print("Warning: No path found through visited cells (shouldn't happen)")

    # Keep trying until we reach goal
    while current_pos != goal:
        reached, _ = move_and_scan(goal)
        if reached:
            print("Goal reached!")
            drone.land()
            break
        else:
            print(f"  Path blocked, replanning...")

    return path, len(visited), False
