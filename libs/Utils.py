import json
import os
from Maze import Maze

def save_maze_to_file(maze, filename="maze.txt"):
    maze_data = {
        'width': maze.width,
        'height': maze.height,
        'walls': [list(wall) for wall in maze.walls]
    }
    with open(filename, 'w') as f:
        json.dump(maze_data, f)
    print(f"Maze saved: {maze.width}x{maze.height} with {len(maze.walls)} walls")

def load_maze_from_file(filename="maze.txt"):
    if not os.path.exists(filename):
        print(f"{filename} not found. Need to discover maze first.")
        return None

    with open(filename, 'r') as f:
        maze_data = json.load(f)

    maze = Maze(maze_data['width'], maze_data['height'])

    for wall in maze_data['walls']:
        cell1 = tuple(wall[0])
        cell2 = tuple(wall[1])
        maze.add_wall(cell1, cell2)

    print(f"Maze loaded: {maze.width}x{maze.height} with {len(maze.walls)} walls")
    return maze

def optimize_path(path):

    if len(path) <= 2:
        return path

    optimized = [path[0]]  # Always keep start point

    for i in range(1, len(path) - 1):
        prev_point = path[i - 1]
        current_point = path[i]
        next_point = path[i + 1]

        # Calculate direction vectors
        dx1 = current_point[0] - prev_point[0]
        dy1 = current_point[1] - prev_point[1]

        dx2 = next_point[0] - current_point[0]
        dy2 = next_point[1] - current_point[1]

        # Keep point if direction changes
        if dx1 != dx2 or dy1 != dy2:
            optimized.append(current_point)

    optimized.append(path[-1])  # Always keep end point

    return optimized
