import tkinter as tk

def pause(self):
    self.matlab_button.config(state = tk.NORMAL)
    self.pause_count += 1
    if self.pause_count % 2 == 0:
        self.log_position("\n")
        self.log_bold("[SYSTEM] ")
        self.log_position("Simulation Paused\n")
    else:
        self.log_position("\n")
        self.log_bold("[SYSTEM] ")
        self.log_position("Simulation Resumed\n")
        self.matlab_button.config(state = tk.DISABLED)
    self.is_paused = not self.is_paused
    self.pause_button.config(text = "Resume" if self.is_paused else "Pause")