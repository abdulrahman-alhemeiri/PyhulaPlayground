import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List
import threading

def alert_race_done():
    messagebox.showinfo("Success", "Object detection race completed successfully!")

class Gui:
    def __init__(self, root, on_start_discovery_callback=None, on_start_race_callback=None):
        self.root = root
        self.root.title("Challenge 2 Solver")
        self.root.geometry("700x600")

        self.on_start_discovery_callback = on_start_discovery_callback
        self.on_start_race_callback = on_start_race_callback

        self._create_widgets()

    def _create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Maze Size
        ttk.Label(main_frame, text="Maze Size (NxM):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.maze_size_entry = ttk.Entry(main_frame, width=50)
        self.maze_size_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.maze_size_entry.insert(0, "4x5")  # Default value

        # Drone Initial Location
        ttk.Label(main_frame, text="Drone Initial Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.initial_location_entry = ttk.Entry(main_frame, width=50)
        self.initial_location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.initial_location_entry.insert(0, "0,0")  # Default value

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
        self.objects_text.insert("1.0", "1,4,East\n2,3,West\n3,4,South\n3,3,East")

        # Start Discovery Button
        self.start_discovery_button = ttk.Button(main_frame, text="Start Discovery", command=self._on_start_discovery_clicked)
        self.start_discovery_button.grid(row=5, column=0, columnspan=1, pady=15)

        # Start Race Button
        self.start_race_button = ttk.Button(main_frame, text="Start Race", command=self._on_start_race_clicked)
        self.start_race_button.grid(row=5, column=1, columnspan=1, pady=15)

        # Risk checkbox
        self.risk_value = tk.BooleanVar(value=False)
        self.risk_checkbox = ttk.Checkbutton(main_frame, text="Risky race?", variable=self.risk_value)
        self.risk_checkbox.grid(row=5, column=2, columnspan=1, pady=15)

        # Objects Found Label
        ttk.Label(main_frame, text="Objects Found:").grid(row=6, column=0, sticky=tk.W, pady=5)

        # Objects Found Output
        self.output_text = scrolledtext.ScrolledText(main_frame, width=50, height=10, state='disabled')
        self.output_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Configure grid weights for resizing
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _on_start_discovery_clicked(self):
        try:
            maze_size = self.maze_size_entry.get()
            width, height = map(int, maze_size.lower().split('x'))

            initial_location = self.initial_location_entry.get()
            x, y = map(int, initial_location.split(','))
            start = (x, y)

            bearing = self.bearing_var.get()

            params = {
                'width': width,
                'height': height,
                'start': start,
                'bearing': bearing
            }

            message = (
                f"Maze Size: {width}x{height}\n"
                f"Start Position: {start}\n"
                f"Drone Initial Bearing: {bearing}\n\n"
                f"This will delete existing maze text file.\n"
                f"Make sure it is safe and you're clear for takeoff.\n\n"
                f"Start discovery?"
            )

            result = messagebox.askokcancel(
                "Start Discovery?",
                message
            )

            if not result:
                return

            self.clear_output()
            self.write_output(f"Started discovery...\n\n")

            self.start_discovery_button.config(state='disabled')
            self.start_race_button.config(state='disabled')
            thread = threading.Thread(target=self._run_discovery_thread, args=(params,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.write_output(f"Error in on_start_discovery_clicked(): {str(e)}\n")

    def _run_discovery_thread(self, params):
        try:
            self.on_start_discovery_callback(params)
            self.write_output_threadsafe(f"Discovery completed.\n\n")
        except Exception as e:
            self.write_output_threadsafe(f"ERROR: {str(e)}\n")
            import traceback
            traceback.print_exc()
        finally:
            # Re-enable buttons from main thread
            self.root.after(0, lambda: self.start_discovery_button.config(state='normal'))
            self.root.after(0, lambda: self.start_race_button.config(state='normal'))

    def _on_start_race_clicked(self):
        initial_location = self.initial_location_entry.get()
        x, y = map(int, initial_location.split(','))
        start = (x, y)

        bearing = self.bearing_var.get()

        objects_input = self.objects_text.get("1.0", tk.END).strip()
        object_data = {}

        for line in objects_input.split('\n'):
            if line.strip():
                parts = [part.strip() for part in line.split(',')]

                if len(parts) != 3:
                    self.write_output(f"Invalid object format: '{line}'. Expected format: x,y,direction\n\n")
                    return

                obj_x = int(parts[0])
                obj_y = int(parts[1])
                obj_direction = parts[2]

                valid_directions = ["North", "West", "South", "East"]
                if obj_direction not in valid_directions:
                    self.write_output(f"Invalid direction '{obj_direction}' in line '{line}'. Must be one of: {valid_directions}\n\n")
                    return

                obj_coordinates_tuple = (obj_x, obj_y)
                if not obj_coordinates_tuple in object_data:
                    object_data[obj_coordinates_tuple] = []
                object_data[obj_coordinates_tuple].append(obj_direction)

        if len(object_data) == 0:
            self.write_output(f"No objects found.\n\n")
            return

        is_risky = self.risk_value.get()

        params = {
            'start': start,
            'bearing': bearing,
            'objects': object_data,
            'is_risky': is_risky
        }

        message = (
            f"Start Position: {start}\n"
            f"Drone Initial Bearing: {bearing}\n"
            f"Objects: {len(object_data)}\n"
            f"Risky run value: {is_risky}\n\n"

            f"Make sure you have finished discovery for the current maze setup.\n"
            f"Make sure it is safe and you're clear for takeoff.\n\n"
            f"Start race?"
        )

        result = messagebox.askokcancel(
            "Start Race?",
            message
        )

        if not result:
            return

        self.clear_output()
        self.write_output(f"Started race...\n\n")

        self.start_race_button.config(state='disabled')
        self.start_discovery_button.config(state='disabled')

        thread = threading.Thread(target=self._run_race_thread, args=(params,))
        thread.daemon = True
        thread.start()

    def _run_race_thread(self, params):
        try:
            self.on_start_race_callback(params)
            self.write_output_threadsafe(f"Race completed.\n\n")
        except Exception as e:
            self.write_output_threadsafe(f"ERROR: {str(e)}\n")
            import traceback
            traceback.print_exc()
        finally:
            # Re-enable buttons from main thread
            self.root.after(0, lambda: self.start_race_button.config(state='normal'))
            self.root.after(0, lambda: self.start_discovery_button.config(state='normal'))

    def write_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def write_output_threadsafe(self, text):
        self.root.after(0, lambda: self.write_output(text))

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state='disabled')

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = Gui(root)
#     root.mainloop()