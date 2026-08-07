import tkinter as tk
from packages import gcodesim_app

# 1. MAIN FUNCTION
def main():
    root = tk.Tk()
    app = gcodesim_app(root) # self >> app
    root.mainloop()

if __name__ == "__main__":
    main()
    