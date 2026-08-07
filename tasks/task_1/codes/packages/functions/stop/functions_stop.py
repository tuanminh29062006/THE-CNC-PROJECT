import tkinter as tk

def stop(self):
    self.matlab_button.config(state = tk.NORMAL)
    self.log_bold("[SYSTEM] ")
    self.log_position("Simulation Stopped\n")
    self.is_running = False
    self.is_g91 = False
    self.run_button.config(state = tk.NORMAL)
    self.pause_button.config(state = tk.DISABLED, text = "Pause")
    self.stop_button.config(state = tk.DISABLED)