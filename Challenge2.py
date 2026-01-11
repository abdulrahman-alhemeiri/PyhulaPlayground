from PyhulaPlayground import Maze, PathFinder, Utils

# start = (0, 0)
# current_bearing = "North"

# fileName = "maze_challenge_2.txt"
# maze = Utils.load_maze_from_file(fileName)
# is_discovery_phase = (maze is None)
#
# drone = Drone(current_bearing)

if is_discovery_phase:
    maze = Maze.Maze(100, 100)
    drone.take_off()
    PathFinder.discover_maze(maze, start, drone)
    Utils.save_maze_to_file(maze, fileName)
    drone.land()
else:
    # objects = {
    #     (1, 0): ["South"],
    #     (2, 1): ["North", "East"],
    #     (2, 0): ["West"]
    # }
    object_coordinates = objects.keys()
    paths = PathFinder.astar_multi_goal_straight_preference(maze, start, object_coordinates)
    optimized_paths = []
    for i in range(len(paths)):
        optimized_path = Utils.optimize_path(paths[i])
        optimized_paths.append(optimized_path)

    is_video_mode = True
    drone.take_off(is_video_mode)
    drone.center_yaw()
    for i in range(len(optimized_paths)):
        drone.traverse_path(optimized_paths[i])
        current_block = drone.get_current_block()
        for object_direction in objects[current_block]:
            print(f"(main): Performing object detection at block: {current_block} - direction: {object_direction}")
            drone.perform_detection(object_direction)

    drone.land(is_video_mode)
