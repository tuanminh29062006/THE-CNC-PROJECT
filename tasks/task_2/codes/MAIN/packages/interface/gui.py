import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from packages.functions import load, reset, pause, stop, run
from packages.log import text, bold, erase, position
from packages.simulation import start, line, linear, graphics, loop, finalize, arc
from packages.interpret.interpret_parse import parse
from packages.history import append
from packages.matlab import m_append, m_code
from packages.status import motor, coordinate
from packages.serial import deliver, connect, receive, ser_parse, update, listen
import re

class gcodesim_app:
    # 1. GUI:
    def __init__(self, root, port = 'COM5', baudrate = 115200):
        self.root = root
        self.root.title("G-Code Simulation")
        self.root.geometry("1800x1000")
        self.parse_pattern = re.compile(r'([GMXYZFIJRP])([+-]?\d+\.?\d*)')
    
        self.parse_pattern_serial = re.compile(
            r"<POS:(?P<g>\d+),(?P<x>[-\d.]+),(?P<y>[-\d.]+),(?P<z>[-\d.]+),"
            r"(?P<status_x>[^,]+),(?P<status_y>[^,]+),(?P<status_z>[^>]+)>"
            r"<STEP:(?P<step_x>[-\d]+),(?P<step_y>[-\d]+),(?P<step_z>[-\d]+)>"
        )

        self.motions = []
        self.widgets()
        self.is_paused = False
        self.is_running = False
        self.pause_count = 1
        self.last_z = None
        self.is_g91 = False
        self.is_unable = False
        # Gỉa sử gia tốc máy của động cơ là đều và 10k m/(s^2):
        self.acceleration = 500.0 # mm/s^2
        self.deceleration = -500.0 # mm/s^2

        # v3.1:
        self.default_fr = 500 # mm/minute
        self.default_fr_g0 = 1500 # mm/minute
        self.baudrate = 115200
    
    def widgets(self):
        # 1.1. LEFT PANEL FRAME:
        left_panel = ttk.Frame(self.root, padding = "10")
        left_panel.pack(side = tk.LEFT, fill = tk.Y, expand = False)
        
        # 1.2. LAYER UPDATE FRAME:
        layer_frame = ttk.LabelFrame(left_panel, text = " Live Position ", padding = (12, 8))
        layer_frame.pack(side = tk.TOP, fill = tk.X, pady = (0, 10), padx = 5)
        layer_frame.columnconfigure((0, 1, 2), weight = 1)
        status_font = ("Consolas", 10)

        # 1.2.1. LABELS IN LAYER UPDATE FRAME:
        """
        self.label = ttk.Label(layer_frame, text = "Layer: --", font = ("Helvetica", 14, "bold"))
        self.label.pack(side = tk.LEFT, padx = (10, 0))
        
        # 1.2.2. PRINT MATLAB CODE:
        self.matlab_button = ttk.Button(layer_frame, text = "Matlab Code", command = self.matlab_code)
        self.matlab_button.pack(side = tk.LEFT, padx = (10, 0))
        """

        x_frame = ttk.Frame(layer_frame)
        x_frame.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.canvas_x = tk.Canvas(x_frame, width = 16, height = 16, highlightthickness = 0)
        self.canvas_x.pack(side = tk.LEFT, padx = (0,6))
        self.square_x = self.canvas_x.create_rectangle(1, 1, 15, 15, fill="#7f8c8d", outline="#000000", width=1.5)
        self.x_label = ttk.Label(x_frame, text = "X: __.___ mm", font = status_font)
        self.x_label.pack(side = tk.LEFT)

        y_frame = ttk.Frame(layer_frame)
        y_frame.grid(row = 0, column = 1, padx = 5, sticky = "w")
        self.canvas_y = tk.Canvas(y_frame, width = 16, height = 16, highlightthickness = 0)
        self.canvas_y.pack(side = tk.LEFT, padx = (100, 0))
        self.square_y = self.canvas_y.create_rectangle(1, 1, 15, 15, fill="#7f8c8d", outline="#000000", width=1.5)
        self.y_label = ttk.Label(y_frame, text = "Y: __.___ mm", font = status_font)
        self.y_label.pack(side = tk.LEFT, padx = (5, 0))

        z_frame = ttk.Frame(layer_frame)
        z_frame.grid(row = 0, column = 2, padx = 5, sticky = "w")
        self.canvas_z = tk.Canvas(z_frame, width = 16, height = 16, highlightthickness = 0)
        self.canvas_z.pack(side = tk.LEFT, padx = (100, 0))
        self.square_z = self.canvas_z.create_rectangle(1, 1, 15, 15, fill="#7f8c8d", outline="#000000", width=1.5)
        self.z_label = ttk.Label(z_frame, text = "Z: __.___ mm", font = status_font)
        self.z_label.pack(side = tk.LEFT, padx = (5, 0))

        # 1.4. RESOLUTION TIME FRAME:
        resolution_frame = ttk.Frame(left_panel)
        resolution_frame.pack(side = tk.TOP, fill = tk.X, pady = 5)

        # 1.4.1. STATIC LABEL IN RESOLUTION TIME FRAME:
        ttk.Label(resolution_frame, text = "Resolution: ").pack(side = tk.LEFT)

        # 1.4.2. ENTRY BOX IN RESOLUTION TIME FRAME AND PORT:
        self.resolution_var = tk.StringVar(value = "0.5")
        self.resolution_entry = ttk.Entry(resolution_frame
                                            , textvariable = self.resolution_var
                                            , width = 8
                                            , justify = "right")
        self.resolution_entry.pack(side = tk.LEFT, padx = 5)
        ttk.Label(resolution_frame, text = "seconds").pack(side = tk.LEFT)

        ttk.Label(resolution_frame, text = "       MCU Port: ").pack(side = tk.LEFT, padx = (0, 0))
        self.port_com = tk.StringVar(value = "COM5")
        self.default_entry = ttk.Entry(resolution_frame
                                            , textvariable = self.port_com
                                            , width = 8
                                            , justify = "right")
        self.default_entry.pack(side = tk.LEFT, padx = 5)

        # 1.3. BUTTON FRAME:
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(side = tk.TOP, fill = tk.X, pady = (10, 5))

        #1.3.1. BUTTONS IN BUTTON FRAME:
        self.load_button = ttk.Button(button_frame, text = "Load G-Code", command = self.functions_load)
        self.load_button.grid(row = 0, column = 1, padx = 5, pady = 5)

        self.connect_button = ttk.Button(button_frame, text = "Connect MCU", command = lambda:self.serial_connect(True))
        self.connect_button.grid(row = 0, column = 0, padx = 5, pady = 5)

        self.run_button = ttk.Button(button_frame, text = "Run", command = self.functions_run, state = tk.DISABLED)
        self.run_button.grid(row = 1, column = 0, padx = 5, pady = 5)

        self.pause_button = ttk.Button(button_frame, text = "Pause", command = self.functions_pause, state = tk.DISABLED)
        self.pause_button.grid(row = 1, column = 1, padx = 5, pady = 5)

        self.stop_button = ttk.Button(button_frame, text = "Stop", command = self.functions_stop, state = tk.DISABLED)
        self.stop_button.grid(row = 1, column = 2, padx = 5, pady = 5)

        self.reset_button = ttk.Button(button_frame, text = "Reset", command = self.functions_reset, state = tk.NORMAL)
        self.reset_button.grid(row = 1, column = 3, padx = 5, pady = 5)

        self.matlab_button = ttk.Button(button_frame, text = "Matlab Code", command = self.matlab_code, state = tk.DISABLED)
        self.matlab_button.grid(row = 1, column = 4, padx = 5, pady = 5)

        # 1.5. GCODE DIRECT TEXT BOX:
        ttk.Label(left_panel, text = "G-Code Script:").pack(anchor = tk.W, pady = (5, 2))
        self.gcode_text = tk.Text(left_panel, width = 55, height = 12, font = ("Courier", 9))
        self.gcode_text.pack(fill = tk.BOTH, expand = True)
        sample_code = (";Load your G-Code file or insert directly here!\n"
                        )
        self.gcode_text.insert(tk.END, sample_code)

        # 1.6. TELEMETRY LOG FOR LIVE TOOL LOCATION:
        ttk.Label(left_panel, text = "Telemetry Log:").pack(anchor = tk.W, pady = (5, 8))
        self.log_text = tk.Text(left_panel
                                , width = 55
                                , height = 10
                                , font = ("Courier", 9)
                                , bg = "black"
                                , fg = "#00FF00")
        self.log_text.pack(fill = tk.BOTH, expand = True)
        self.log_text.tag_config("bold_style", font=("Courier", 9, "bold"))
        sample_log = ("Live Tool Position:\n")
        self.log_text.insert(tk.END, sample_log, "bold_style")

        # 1.7. RIGHT PANEL FRAME:
        right_panel = ttk.Frame(self.root, padding = "10")
        right_panel.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)

        # 1.8. BUILD THE MATPLOTLIB FIGURE:
        self.fig, self.ax = plt.subplots(figsize = (10, 10), dpi = 100)
        self.ax.set_title("TOOL PATH")
        self.ax.set_xlabel("X (mm)")
        self.ax.set_ylabel("Y (mm)")
        self.ax.grid(True)
        self.ax.set_aspect('equal')#, adjustable = 'box')

        # 1.8.1. SET UP THE 3 LINES PLOT:
        self.feed_motion, = self.ax.plot([], [], 'b-', alpha = 0.8, linewidth = 2, label = "Feed Motion")
        self.g0, = self.ax.plot([], [], 'k--', alpha = 0.3, linewidth = 1, label = "G0")
        self.tool_head, = self.ax.plot([], [], 'ro', markersize = 8, label = "Tool Head", zorder = 5)
        self.ax.legend(loc = "best")

        # 1.8.2. CONVERT FIGURE INTO WIDGETS:
        self.canvas = FigureCanvasTkAgg(self.fig, master = right_panel)
        self.canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
    
    # 1.9. WIDGET FUNCTIONS
    # 1.9.1. FUNCTIONS:
    def functions_load(self):
        load(self)
        parse(self)

    def functions_pause(self):
        pause(self)

    def functions_stop(self):
        stop(self)

    def functions_reset(self):
        reset(self)
                                      
    def functions_run(self):
        run(self)

    # 1.9.2. G-CODE INTERPRET:
    def interpret_parse(self):
        parse(self)   

    # 1.9.3. LOG TEXT:
    def log(self, message):
        text(self, message)
    
    def log_bold(self, message):
        bold(self, message)
    
    def log_erase(self):
        erase(self)
    
    def log_position(self, message):
        position(self, message)
    
    # 1.10. START SIMULATION
    def simulation_start(self):
        start(self)

    def simulation_line(self, index, d_x, d_y, d_z, d_feed):
        line(self, index, d_x, d_y, d_z, d_feed)

    def simulation_linear(self, index, ini_x, ini_y, ini_z,
            next_x, next_y, next_z, g_cmd,
            feed_rate, velocity,
            elapsed, distance, first_line):
        linear(self, index, ini_x, ini_y, ini_z,
            next_x, next_y, next_z, g_cmd,
            feed_rate, velocity,
            elapsed, distance, first_line)
    
    def simulation_arc(self, index, ini_x, ini_y, ini_z,
                        next_x, next_y, next_z, g_cmd,
                        feed_rate, velocity,
                        elapsed, arc_start,
                        arc_length, arc_rotation, 
                        ori_x, ori_y, radius, first_line):
        arc(self, index, ini_x, ini_y, ini_z,
            next_x, next_y, next_z, g_cmd,
            feed_rate, velocity,
            elapsed, arc_start,
            arc_length, arc_rotation, 
            ori_x, ori_y, radius, first_line)
    """
    def simulation_graphics(self, elapsed, g_cmd, index):
        graphics(self, elapsed, g_cmd, index)
    """
    def simulation_graphics(self):
        graphics(self)
    
    def simulation_loop(self, callback_function, *args):
        loop(self, callback_function, *args)
    
    def simulation_finalize(self, index, n_x, n_y, n_z, vel_j_x, vel_j_y, vel_j_z, acce_j_x, acce_j_y, acce_j_z, n_feed, g_cmd):
        finalize(self, index, n_x, n_y, n_z, vel_j_x, vel_j_y, vel_j_z, acce_j_x, acce_j_y, acce_j_z, n_feed, g_cmd)
    
    # 1.11. APPEND HISTORY
    """
    def history_append(self, append_x, append_y, append_z, velocity_j_x, velocity_j_y, velocity_j_z, acce_j_x, acce_j_y, acce_j_z, g_cmd):
        append(self, append_x, append_y, append_z, velocity_j_x, velocity_j_y, velocity_j_z, acce_j_x, acce_j_y, acce_j_z, g_cmd)
    """
    def history_append(self, append_x, append_y, append_z, g_cmd):
        append(self, append_x, append_y, append_z, g_cmd)
        
        
    # 1.12. MATLAB
    """
    def matlab_append(self, m_x, m_y):
        m_append(self, m_x, m_y)
    """   
    def matlab_append(self, m_x, m_y, m_z):
        m_append(self, m_x, m_y, m_z)
    
    def matlab_code(self):
        m_code(self)

    # 1.13. STATUS
    def status_motor(self, axis: str, color: str, outline: str = "#000000"):
        motor(self, axis, color, outline)

    def status_coordinate(self, x: float, y: float, z: float):
        coordinate(self, x, y, z)

    # 1.14. SERIAL
    def serial_connect(self, log_boolean):
        connect(self, log_boolean)

    def serial_deliver(self):
        deliver(self)

    def serial_receive(self, deliver):
        receive(self, deliver)

    def serial_parse(self, line):
        return ser_parse(self, line)

    def serial_update(self, line):
        update(self, line)

    def serial_listen(self):
        listen(self)