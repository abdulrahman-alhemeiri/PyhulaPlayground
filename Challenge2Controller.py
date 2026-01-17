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

        self.on_progress("=== Challenge 2 Maze Discovery Started ===\n")
        self.on_progress(f"Start: {start}, Bearing: {bearing}\n\n")

        self.maze = Maze.Maze(width, height)

        challenge_number = 2
        phase_number = 1
        self.drone = Drone(bearing, challenge_number, phase_number)

        self.on_progress("Taking off...\n")
        self.drone.take_off()

        self.on_progress("Starting maze discovery...\n")
        PathFinder.discover_maze(self.maze, start, self.drone)

        self.on_progress("Saving maze to file...\n")
        Utils.save_maze_to_file(self.maze, file_name)

        self.on_progress("Landing...\n")
        self.drone.land()

        self.on_progress("Discovery complete!\n")

        return

    def on_start_race(self, params):
        start = params['start']
        bearing = params['bearing']
        objects = params['objects']
        is_risky = params['is_risky']
        self.num_objects = sum(len(v) for v in objects.values())

        self.on_progress("=== Challenge 2 Maze Solving (Race) Started ===\n")
        self.on_progress(f"Start: {start}, Bearing: {bearing}\n")
        self.on_progress(f"Objects to find: {self.num_objects}\n")
        self.on_progress(f"Risky run value: {is_risky}\n\n")

        self.on_progress("loading maze...\n")
        maze = Utils.load_maze_from_file(file_name)
        maze_file_not_found = (maze is None)
        if maze_file_not_found:
            self.on_progress("\n***WARNING***: Maze file not found.\n")
            return

        self.found_count = 0

        challenge_number = 2
        phase_number = 2
        self.drone = Drone(bearing, challenge_number, phase_number, is_risky)
        object_coordinates = objects.keys()

        self.on_progress("Calculating optimal path...\n")
        paths = PathFinder.astar_multi_goal_straight_preference(maze, start, object_coordinates)
        self.on_progress(f"Path calculated: {len(paths)} segments\n\n")
        paths = optimized_paths(paths)

        self.on_progress("Taking off...\n")
        self.drone.take_off()

        for i in range(len(paths)):
            self.on_progress(f"Traversing segment {i + 1}/{len(paths)}...\n")
            self.drone.traverse_path(paths[i])

            # current_block = self.drone.get_current_block()
            # if current_block[0] >= maze.width:
            #     current_block[0] = maze.width - 1
            # if current_block[1] >= maze.height:
            #     current_block[1] = maze.height - 1

            # After:
            current_block = self.drone.get_current_block()
            current_block_x = current_block[0]
            current_block_y = current_block[1]

            # Clamp coordinates to maze bounds
            if current_block_x >= maze.width:
                current_block_x = maze.width - 1
            if current_block_y >= maze.height:
                current_block_y = maze.height - 1

            current_block = (current_block_x, current_block_y)

            for object_direction in objects[current_block]:
                self.on_progress(f"Performing object detecting at {current_block} facing {object_direction}...\n")
                print(f"(main): Performing object detection at block: {current_block} - direction: {object_direction}")
                self.drone.perform_detection(object_direction, on_object_found=self.on_object_found)

        self.on_progress("Landing...\n")
        self.drone.land()

        self.on_progress("\n=== Race Complete ===\n")

    def on_object_found(self, object_name, direction, current_block):
        self.found_count += 1
        msg = f"{self.found_count}. Found a {object_name} at ({current_block[0]},{current_block[1]}) in {direction} direction\n"
        self.on_progress(msg)
        if self.found_count == self.num_objects:
            self.gui.root.after(0, Challenge2Gui.alert_race_done)

    def on_progress(self, message):
        if self.gui:
            self.gui.write_output_threadsafe(message)

if __name__ == "__main__":
    controller = Challenge2Controller()
    controller.run()