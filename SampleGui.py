import tkinter as tk

# 1. Create the main application window
root = tk.Tk()
root.title("Simple GUI")
root.geometry("300x100") # Set the window size

# 2. Add a widget (a label)
label = tk.Label(root, text="Hello, World! This is a simple Python GUI.")
label.pack(pady=20) # Add padding to the label

# 3. Add a button widget
def on_button_click():
    label.config(text="Button clicked! Hello again!")

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# 4. Enter the main event loop
root.mainloop()