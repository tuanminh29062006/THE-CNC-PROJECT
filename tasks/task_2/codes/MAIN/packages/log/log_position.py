import tkinter as tk

def position(self, message):
    self.log_text.insert(tk.END, message)
    self.log_text.see(tk.END)