"""Main application controller"""
import tkinter as tk
from PyhulaPlayground import Maze, PathFinder, Utils
from PyhulaPlayground.Challenge2Gui import Gui
import PyhulaPlayground.Challenge2Gui as Challenge2Gui
from PyhulaPlayground.Drone import Drone
from PyhulaPlayground.Utils import optimized_paths

file_name = "maze_challenge_1.txt"

class Challenge2Controller:
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
        self.drone.take_off()
        PathFinder.discover_maze(self.maze, start, self.drone)
        Utils.save_maze_to_file(self.maze, file_name)
        self.drone.land()
        return

    def on_start_race(self, params):
        start = params['start']
        bearing = params['bearing']
        goal = params['goal']

        self.gui.write_output("=== Challenge 1 Maze Solving (Race) Started ===\n")
        self.gui.write_output(f"Start: {start}, Bearing: {bearing}\n")
        self.gui.write_output(f"Goal: {goal}\n\n")

        maze = Utils.load_maze_from_file(file_name)
        maze_file_not_found = (maze is None)
        if maze_file_not_found:
            self.gui.write_output("\n***WARNING***: Maze file not found.\n")
            return

        self.drone = Drone(bearing)
        path = PathFinder.astar_straight_preference(maze, start, goal)
        optimized_path = Utils.optimized_path(path)

        self.drone.take_off()
        # self.drone.center_yaw() # TODO: Risk flag
        self.drone.traverse_path(optimized_path)
        self.drone.land()

    def on_progress(self, message):
        """Callback for progress updates"""
        # Optional: update GUI with progress
        pass

if __name__ == "__main__":
    controller = Challenge2Controller()
    controller.run()