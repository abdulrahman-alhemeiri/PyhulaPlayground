"""Main application controller"""
import tkinter as tk
from libs import Utils, PathFinder, Maze
from libs.Challenge2Gui import Gui
import libs.Challenge2Gui as Challenge2Gui
from libs.Drone import Drone
from libs.Utils import optimized_paths

file_name = "maze_challenge_2.txt"

class Challenge2Controller:
    def __init__(self):
        self.num_objects = 0
        self.gui = None
        self.maze = None
        self.drone = None
        self.object_map = {}
        self.found_count = 0

    def run(self):
        root = tk.Tk()
        self.gui = Gui(root, self.on_start_discovery, self.on_start_race)
        root.mainloop()

    def on_start_discovery(self, params):
        width = params['width']
        height = params['height']
        start = params['start']
        bearing = params['bearing']

        self.gui.write_output("=== Challenge 2 Maze Discovery Started ===\n")
        self.gui.write_output(f"Start: {start}, Bearing: {bearing}\n")

        self.maze = Maze.Maze(width, height)
        self.drone.take_off()
        PathFinder.discover_maze(self.maze, start, self.drone)
        Utils.save_maze_to_file(self.maze, file_name)
        self.drone.land()
        return

    def on_start_race(self, params):
        start = params['start']
        bearing = params['bearing']
        objects = params['objects']
        self.num_objects = len(objects)

        self.gui.write_output("=== Challenge 2 Maze Solving (Race) Started ===\n")
        self.gui.write_output(f"Start: {start}, Bearing: {bearing}\n")
        self.gui.write_output(f"Objects to find: {self.num_objects}\n\n")

        maze = Utils.load_maze_from_file(file_name)
        maze_file_not_found = (maze is None)
        if maze_file_not_found:
            self.gui.write_output("\n***WARNING***: Maze file not found.\n")
            return

        self.found_count = 0

        self.drone = Drone(bearing)
        object_coordinates = objects.keys()
        paths = PathFinder.astar_multi_goal_straight_preference(maze, start, object_coordinates)
        paths = optimized_paths(paths)

        is_video_mode = True
        self.drone.take_off(is_video_mode)
        self.drone.center_yaw()

        for i in range(len(paths)):
            self.drone.traverse_path(paths[i])
            current_block = self.drone.get_current_block()
            for object_direction in objects[current_block]:
                print(f"(main): Performing object detection at block: {current_block} - direction: {object_direction}")
                self.drone.perform_detection(object_direction, on_object_found=self.on_object_found)

        self.drone.land(is_video_mode)

        #
        # # Initialize object map (position -> name mapping)
        # # You can load this from config or let drone detect names
        # for i, pos in enumerate(object_coords, 1):
        #     self.object_map[pos] = f"Object{i}"  # Default names
        #
        #
        # # Try to load existing maze
        # self.maze = load_maze_from_file("walls.txt")
        #
        # if self.maze and (self.maze.width != width or self.maze.height != height):
        #     self.gui.write_output("Warning: Cached maze dimensions don't match. Creating new maze.\n")
        #     self.maze = None
        #
        # if self.maze:
        #     self.gui.write_output("Loaded existing maze from file.\n")
        #     self.run_pathfinding_phase(start, object_coords)
        # else:
        #     self.gui.write_output("No cached maze. Starting discovery...\n")
        #     self.maze = Maze(width, height)
        #     self.run_discovery_phase(start, object_coords)

    def run_discovery_phase(self, start, object_coords):
        """Run maze discovery with drone"""
        # self.drone = Drone()
        #
        # # Set up object names in drone (so it can report them)
        # self.drone.detected_objects = self.object_map
        #
        # goal = (self.maze.width - 1, self.maze.height - 1)  # Example goal
        #
        # try:
        #     path, visited = discover_maze_with_objects_fast(
        #         self.maze,
        #         start,
        #         self.drone,
        #         object_coords,
        #         goal,
        #         on_object_found=self.on_object_found,
        #         on_progress=self.on_progress
        #     )
        #
        #     self.gui.write_output(f"\n=== Discovery Complete ===\n")
        #     self.gui.write_output(f"Cells explored: {visited}\n")
        #
        #     # Save discovered maze
        #     save_maze_to_file(self.maze, "walls.txt")
        #     self.gui.write_output("Maze saved to walls.txt\n")
        #
        # except Exception as e:
        #     self.gui.write_output(f"Error during discovery: {str(e)}\n")
        return

    def run_pathfinding_phase(self, start, object_coords):
        # """Run pathfinding with known maze"""
        # self.gui.write_output("Calculating optimal path...\n")
        #
        # # Try to load cached path
        # segments = load_path_segments_from_file("path_segments.txt")
        #
        # if segments is None:
        #     self.gui.write_output("No cached path. Calculating...\n")
        #     segments = astar_multi_goal_straight_preference(self.maze, start, object_coords)
        #
        #     if segments:
        #         save_path_segments_to_file(segments, "path_segments.txt")
        #         self.gui.write_output("Path calculated and saved.\n")
        # else:
        #     self.gui.write_output("Loaded cached path.\n")
        #
        # if segments:
        #     self.execute_path(segments)
        # else:
        #     self.gui.write_output("No valid path found!\n")
        return

    def execute_path(self, segments):
        # """Execute the path segments with drone"""
        # self.drone = Drone()
        # self.drone.detected_objects = self.object_map
        #
        # self.gui.write_output(f"\nExecuting path with {len(segments)} segments...\n")
        #
        # for i, segment in enumerate(segments, 1):
        #     self.gui.write_output(f"\nSegment {i}: Moving to goal...\n")
        #     optimized = optimize_path(segment)
        #
        #     for waypoint in optimized[1:]:
        #         self.drone.move_to_block(waypoint[0], waypoint[1])
        #
        #     # Check if we reached an object
        #     final_pos = segment[-1]
        #     if final_pos in self.object_map:
        #         self.drone.perform_360_object_detection()
        #         self.on_object_found(self.object_map[final_pos], final_pos)
        #
        # self.gui.write_output("\n=== Path Execution Complete ===\n")
        return

    def on_object_found(self, object_name, direction, current_block):
        """Callback when object is detected"""
        self.found_count += 1
        self.gui.write_output(f"{self.found_count}. Found a {object_name} at ({current_block[0]},{current_block[1]}) in {direction} direction\n")
        if self.found_count == self.num_objects:
            Challenge2Gui.alert_race_done()

    def on_progress(self, message):
        """Callback for progress updates"""
        # Optional: update GUI with progress
        pass


if __name__ == "__main__":
    controller = Challenge2Controller()
    controller.run()