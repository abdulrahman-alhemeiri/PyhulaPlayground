"""Main application controller"""
import tkinter as tk
from PyhulaPlayground import Maze, PathFinder, Utils
from PyhulaPlayground.Challenge2Gui import Gui
import PyhulaPlayground.Challenge2Gui as Challenge2Gui
from PyhulaPlayground.Drone import Drone
from PyhulaPlayground.Utils import optimized_paths

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
        self.drone = Drone(bearing)
        self.drone.take_off()
        PathFinder.discover_maze(self.maze, start, self.drone)
        Utils.save_maze_to_file(self.maze, file_name)
        self.drone.land()
        return

    def on_start_race(self, params):
        start = params['start']
        bearing = params['bearing']
        objects = params['objects']
        self.num_objects = sum(len(v) for v in objects.values())

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
        # self.drone.center_yaw() # TODO: Risk flag

        for i in range(len(paths)):
            self.drone.traverse_path(paths[i])

            current_block = self.drone.get_current_block()
            if current_block[0] >= maze.width:
                current_block[0] = maze.width - 1
            if current_block[1] >= maze.height:
                current_block[1] = maze.height - 1

            for object_direction in objects[current_block]:
                print(f"(main): Performing object detection at block: {current_block} - direction: {object_direction}")
                self.drone.perform_detection(object_direction, on_object_found=self.on_object_found)

        self.drone.land(is_video_mode)

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