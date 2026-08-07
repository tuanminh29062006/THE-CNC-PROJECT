import tkinter as tk
from tkinter import filedialog

def load(self):
    #self.run_button.config(state = tk.NORMAL)
    file_path = filedialog.askopenfilename()
    if not file_path:
        #self.gcode_text.delete(1.0, tk.END)
        self.log_erase()
        self.log_bold(f"[ERROR] Failed to load file\n")
        return
    try: 
        with open(file_path, "r", encoding='utf-8') as file:
            self.log_erase()
            self.gcode_text.delete(1.0, tk.END)
            self.gcode_text.insert(tk.END, file.read())
        self.log_bold("[SYSTEM] G-Code file has been successfully loaded\n")
    except Exception as e:
        self.log_erase()
        self.gcode_text.delete(1.0, tk.END)
        self.log_bold(f"[ERROR] Failed to load file due to: \n>         {e}\n")
        