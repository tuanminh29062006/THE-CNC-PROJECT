import tkinter as tk
from tkinter import filedialog

def load(self):
    #self.run_button.config(state = tk.NORMAL)
    file_path = filedialog.askopenfilename()
    if not file_path:
        #self.gcode_text.delete(1.0, tk.END)
        self.log(f"Failed to load file\n")
        return
    try: 
        with open(file_path, "r", encoding='utf-8') as file:
            self.gcode_text.delete(1.0, tk.END)
            self.gcode_text.insert(tk.END, file.read())
        self.log("G-Code file has been successfully loaded\n")
    except Exception as e:
        self.gcode_text.delete(1.0, tk.END)
        self.log(f"Failed to load file due to: \n>> {e}\n")
        