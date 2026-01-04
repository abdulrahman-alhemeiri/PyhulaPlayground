import Maze
import Drone
import PathFinder
import Utils

maze = Maze.Maze(4,3)
start = (0, 0)
goal = (0, 1)
object_coordinates = [(0, 2), (2, 0), (3, 2)]

drone = Drone.Drone()
is_phase_3_video_mode = True
drone.take_off(is_phase_3_video_mode)

# drone.center_at_current_block()
drone.center_yaw()

path, length, goal_not_reached = PathFinder.discover_maze_with_objects_fast(maze, start, drone, object_coordinates, goal)
if goal_not_reached:
    optimized_path = Utils.optimize_path(path)
    drone.traverse_path(optimized_path)

drone.land(is_phase_3_video_mode)
