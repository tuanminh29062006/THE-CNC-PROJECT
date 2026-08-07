import tkinter as tk

def text(self, message):
    self.log_text.delete(1.0, tk.END)
    #space = ("------------------\n")
    system = ("[SYSTEM] ")
    #self.log_text.insert(tk.END, space)
    self.log_text.insert(tk.END, system, "bold_style")
    self.log_text.insert(tk.END, message)
    self.log_text.see(tk.END)