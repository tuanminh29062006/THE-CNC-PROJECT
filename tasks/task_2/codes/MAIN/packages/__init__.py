import tkinter as tk
import sys
from .interface.gui import gcodesim_app

# 0. FIX BLURRINESS DISPLAY (High DPI Awareness)
try:
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print("Could not set DPI awareness:", e)
