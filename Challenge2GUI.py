import tkinter as tk
from tkinter import ttk, scrolledtext


class DroneMazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Maze Solver")
        self.root.geometry("700x600")

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Maze Size
        ttk.Label(main_frame, text="Maze Size (NxM):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.maze_size_entry = ttk.Entry(main_frame, width=50)
        self.maze_size_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.maze_size_entry.insert(0, "5x5")  # Default value

        # Drone Initial Location
        ttk.Label(main_frame, text="Drone Initial Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.initial_location_entry = ttk.Entry(main_frame, width=50)
        self.initial_location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.initial_location_entry.insert(0, "0,2")  # Default value

        # Drone Initial Bearing (Dropdown)
        ttk.Label(main_frame, text="Drone Initial Bearing:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bearing_var = tk.StringVar()
        self.bearing_dropdown = ttk.Combobox(main_frame, textvariable=self.bearing_var,
                                             values=["North", "West", "South", "East"],
                                             state="readonly", width=47)
        self.bearing_dropdown.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.bearing_dropdown.set("North")  # Default value

        # Objects Locations
        ttk.Label(main_frame, text="Objects Locations (x,y,direction):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.objects_text = scrolledtext.ScrolledText(main_frame, width=50, height=6)
        self.objects_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # Default values
        self.objects_text.insert("1.0", "1,2,North\n2,3,West\n3,4,South\n3,3,East")

        # Start Button
        self.start_button = ttk.Button(main_frame, text="Start", command=self.on_start_clicked)
        self.start_button.grid(row=5, column=0, columnspan=2, pady=15)

        # Objects Found Label
        ttk.Label(main_frame, text="Objects Found:").grid(row=6, column=0, sticky=tk.W, pady=5)

        # Objects Found Output
        self.output_text = scrolledtext.ScrolledText(main_frame, width=50, height=10, state='disabled')
        self.output_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Configure grid weights for resizing
        main_frame.columnconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

    def on_start_clicked(self):
        """Handle Start button click"""
        # 1. Read inputs
        maze_size = self.maze_size_entry.get()
        initial_location = self.initial_location_entry.get()
        bearing = self.bearing_var.get()
        objects_input = self.objects_text.get("1.0", tk.END).strip()

        # 2. Parse inputs
        try:
            # Parse maze size (e.g., "5x5" -> width=5, height=5)
            width, height = map(int, maze_size.lower().split('x'))

            # Parse initial location (e.g., "0,2" -> (0, 2))
            x, y = map(int, initial_location.split(','))
            start = (x, y)

            # Parse objects locations
            objects = []
            for line in objects_input.split('\n'):
                if line.strip():
                    obj_x, obj_y = map(int, line.strip().split(','))
                    objects.append((obj_x, obj_y))

            # 3. Clear previous output
            self.clear_output()

            # 4. Write to output
            self.write_output("=== Maze Solving Started ===\n")
            self.write_output(f"Maze Size: {width}x{height}\n")
            self.write_output(f"Start Position: {start}\n")
            self.write_output(f"Initial Bearing: {bearing}\n")
            self.write_output(f"Objects to Find: {objects}\n\n")

            # 5. Run your drone maze solving algorithm here
            # This is where you'd call your actual functions
            self.run_maze_solver(width, height, start, bearing, objects)

        except Exception as e:
            self.write_output(f"Error: {str(e)}\n")

    def run_maze_solver(self, width, height, start, bearing, objects):
        """
        This is where you integrate your actual maze solving code.
        For now, it's a simulation.
        """
        # Simulate finding objects
        import time

        # Example: Simulate discovering objects
        discovered_objects = [
            ("Tank", (3, 3)),
            ("Tree", (1, 2)),
            ("House", (3, 4))
        ]

        for obj_name, obj_pos in discovered_objects:
            # Simulate some processing time
            self.root.update()  # Update GUI

            # Write output
            self.write_output(f"{len(self.get_found_objects()) + 1}. {obj_name} {obj_pos[0]},{obj_pos[1]}\n")

        self.write_output("\n=== Maze Solving Complete ===\n")

    def write_output(self, text):
        """Write text to the output area"""
        self.output_text.config(state='normal')  # Enable editing
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)  # Scroll to bottom
        self.output_text.config(state='disabled')  # Disable editing

    def clear_output(self):
        """Clear the output area"""
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state='disabled')

    def get_found_objects(self):
        """Get list of currently found objects from output"""
        output = self.output_text.get("1.0", tk.END)
        # Parse output to count found objects (simple example)
        lines = [line for line in output.split('\n') if line.strip() and line[0].isdigit()]
        return lines
