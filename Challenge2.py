import Maze
from Drone import Drone
import PathFinder
import Utils

maze = Maze.Maze(4,3)
start = (0, 0)
object_coordinates = [(2, 0), (3, 1), (2, 1)]
object_directions= {
    (2, 0): "West",
    (2, 1): "East",
    (3, 1): "West"
}
current_bearing = "North"

paths = Utils.load_paths_from_file("challange_2_paths.txt")

drone = Drone(current_bearing)
is_phase_3_video_mode = True
drone.take_off(is_phase_3_video_mode)
drone.center_yaw()

if paths is None:
    PathFinder.discover_maze(maze, start, drone)
    paths = PathFinder.astar_multi_goal_straight_preference(maze, start, object_coordinates)
    optimized_paths = []
    for i in range(len(paths)):
        optimized_path = Utils.optimize_path(paths[i])
        optimized_paths.append(optimized_path)
    Utils.save_paths_to_file(optimized_paths)
else:
    for i in range(len(paths)):
        drone.traverse_path(paths[i])
        current_block = drone.get_current_block()
        drone.perform_detection(object_directions[tuple(current_block)])
        print(f"(main): Performing object detection at block {tuple(current_block)} which has direction {object_directions[tuple(current_block)]}")

drone.land(is_phase_3_video_mode)
