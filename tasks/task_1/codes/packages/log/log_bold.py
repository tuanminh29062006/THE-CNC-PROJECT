import tkinter as tk

def bold(self, message):
    self.log_text.insert(tk.END, message, "bold_style")
    self.log_text.see(tk.END)