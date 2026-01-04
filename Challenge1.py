import Maze
import Drone
import PathFinder
import Utils

maze = Maze.Maze(4,3)
start = (0, 0)
goal = (2, 0)

path = Utils.load_path_from_file("path.txt")

drone = Drone.Drone()
drone.take_off()
# drone.center_at_current_block()
# drone.center_yaw()

if path is  None:
    PathFinder.discover_maze(maze, start, drone)
    path = PathFinder.astar_straight_preference(maze, start, goal)
    optimized_path = Utils.optimize_path(path)
    Utils.save_path_to_file(optimized_path)
else:
    drone.traverse_path(path)

drone.land()
