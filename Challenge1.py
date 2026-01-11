from PyhulaPlayground import Maze, Drone, PathFinder, Utils

start = (0, 0)

fileName = "maze_challenge_1.txt"
maze = Utils.load_maze_from_file(fileName)
is_discovery_phase = (maze is None)
drone = Drone.Drone()

if is_discovery_phase:
    maze = Maze.Maze(100, 100)
    drone.take_off()
    PathFinder.discover_maze(maze, start, drone)
    Utils.save_maze_to_file(maze, fileName)
else:
    goal = (0, 4)
    path = PathFinder.astar_straight_preference(maze, start, goal)
    optimized_path = Utils.optimized_path(path)
    drone.take_off()
    drone.traverse_path(optimized_path)

drone.land()
