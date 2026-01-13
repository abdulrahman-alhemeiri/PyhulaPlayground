import tkinter as tk
from PyhulaPlayground import Maze, PathFinder, Utils
from PyhulaPlayground.Challenge2Gui import Gui
import PyhulaPlayground.Challenge2Gui as Challenge2Gui
from PyhulaPlayground.Drone import Drone
from PyhulaPlayground.Utils import optimized_paths

file_name = "maze_challenge_1.txt"

class Challenge1Controller:
    def __init__(self):
        self.gui = None
        self.maze = None
        self.drone = None

    def run(self):
        root = tk.Tk()
        self.gui = Gui(root, self.on_start_discovery, self.on_start_race)
        root.mainloop()

    def on_start_discovery(self, params):
        width = params['width']
        height = params['height']
        start = params['start']
        bearing = params['bearing']

        self.gui.write_output("=== Challenge 1 Maze Discovery Started ===\n")
        self.gui.write_output(f"Start: {start}, Bearing: {bearing}\n")

        self.maze = Maze.Maze(width, height)

        self.drone = Drone(bearing)

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
        goal = params['goal']

        self.on_progress("=== Challenge 1 Maze Solving (Race) Started ===\n")
        self.on_progress(f"Start: {start}, Bearing: {bearing}\n")
        self.on_progress(f"Goal: {goal}\n\n")

        self.on_progress("loading maze...\n")
        maze = Utils.load_maze_from_file(file_name)
        maze_file_not_found = (maze is None)
        if maze_file_not_found:
            self.gui.write_output("\n***WARNING***: Maze file not found.\n")
            return

        self.drone = Drone(bearing)

        self.on_progress("Calculating optimal path...\n")
        path = PathFinder.astar_straight_preference(maze, start, goal)
        optimized_path = Utils.optimized_path(path)

        self.on_progress("Taking off...\n")
        self.drone.take_off()
        # self.drone.center_yaw() # TODO: Risk flag

        self.on_progress(f"Traversing optimal path\n")
        self.drone.traverse_path(optimized_path)

        self.on_progress("Landing...\n")
        self.drone.land()

        self.on_progress("\n=== Race Complete ===\n")

    def on_progress(self, message):
        if self.gui:
            self.gui.write_output_threadsafe(message)

if __name__ == "__main__":
    controller = Challenge2Controller()
    controller.run()