import tkinter as tk
from tkinter import messagebox
import math

def start(self):
    try:
        self.resolution_time = float(self.resolution_var.get())
        if self.resolution_time <= 0 or self.resolution_time < 0.01: raise ValueError
        line = f"t: {self.resolution_time}"
        self.serial_gcode.append(line)
    except ValueError:
        self.log_erase()
        self.log_bold("[ERROR] Resolution time must be a positive number and Greater than or equal 10(ms).\n")
        messagebox.showerror("ERROR", "Resolution time must be a Positive Number and Greater than or equal 10(ms).")
        return
    
    self.is_running = True # Điều kiện cần
    self.interpret_parse()

    if not self.motions: # Điều kiện đủ
        self.is_running = False
        self.log_bold("[ERROR] Nothing to run.\n")
        return
    
    for find_g91 in self.motions:
        g_cmd = find_g91.get('G')
        if g_cmd == 91:
            self.is_g91 = True
    
    #self.current_layer = 0
    self.last_z = None
    self.history_x, self.history_y, self.history_z = [0.0], [0.0], [0.0]
    self.travel_x, self.travel_y, self.travel_z = [0.0], [0.0], [0.0]
    self.velocity_x, self.velocity_y, self.velocity_z = [0.0], [0.0], [0.0]
    self.curent_x = 0.0
    self.curent_y = 0.0
    self.curent_z = 0.0

    # Matlab
    self.matlab_x = [0.0]
    self.matlab_y = [0.0]
    self.matlab_z = [0.0]
    
    # Reset ax lim
    self.all_x = [0.0]
    self.all_y = [0.0]
    self.all_i = [0.0]
    self.all_j = [0.0]
    self.dia_max = 0.0
    self.low_y = 0.0
    self.high_y = 0.0
    self.low_x = 0.0
    self.high_x = 0.0

    self.past_sum_x = 0.0
    self.sum_x = 0.0
    self.past_sum_y = 0.0
    self.sum_y = 0.0
    self.now_x = 0.0
    self.now_y = 0.0

    # Reset linear
    self.is_equal = False
    self.is_less = False
    self.is_greater = False
    self.line_x_done = False
    self.line_y_done = False
    self.line_z_done = False
    self.cos_x = 0.0
    self.cos_y = 0.0
    self.cos_z = 0.0
    self.t_acce, self.t_stable, self.t_dece, self.total_time = 0.0, 0.0, 0.0, 0.0
    self.vector_x, self.vector_y, self.vector_z = 0.0, 0.0, 0.0

    for index, line in enumerate(self.motions):
        if index == 0:
            self.now_x = 0.0
            self.now_y = 0.0
            self.sum_x = 0.0
            self.sum_y = 0.0
        
        part_x = line.get('X', 0.0)
        part_y = line.get('Y', 0.0)
                    
        if line['C'] == 91:
            part_x += self.now_x
            part_y += self.now_y
        
        
        self.sum_x += (part_x - self.now_x)
        self.sum_y += (part_y - self.now_y)
        self.now_x = part_x
        self.now_y = part_y
            
        
        if index == 0:
            # X
            if self.sum_x >= 0.0:
                self.high_x = self.sum_x
                self.low_x = 0.0
            else:
                self.low_x = self.sum_x
                self.high_x = 0.0
            
            # Y
            if self.sum_y >= 0.0:
                self.high_y = self.sum_y
                self.low_y = 0.0
            else:
                self.low_y = self.sum_y
                self.high_y = 0.0
        else:
            # X
            if self.sum_x > self.high_x:
                self.high_x = self.sum_x
            elif self.sum_x < self.low_x:
                self.low_x = self.sum_x

            # Y
            if self.sum_y > self.high_y:
                self.high_y = self.sum_y
            elif self.sum_y < self.low_y:
                self.low_y = self.sum_y
        
    """
    if not self.is_g91:
        self.all_x = [part_x.get('X', 0.0) for part_x in self.motions] + [0.0]
        self.all_y = [part_y.get('Y', 0.0) for part_y in self.motions] + [0.0]
    else:
        for index, part_x in enumerate(self.motions):
            incremental_x = part_x.get('X', 0.0)
            if index == 0:
                first_x = part_x.get('X', 0.0)
                self.all_x.append(first_x)
            else:
                next_x = incremental_x + self.all_x[-1]
                self.all_x.append(next_x)
            if index == (len(self.motions) - 1):
                empty = [0.0]
                self.all_x += empty

        for index, part_y in enumerate(self.motions):
            incremental_y = part_y.get('Y', 0.0)
            if index == 0:
                first_y = part_y.get('Y', 0.0)
                self.all_y.append(first_y)
            else:
                next_y = incremental_y + self.all_y[-1]
                self.all_y.append(next_y)
            if index == (len(self.motions) - 1):
                empty = [0.0]
                self.all_y += empty
    """
    self.all_i = [part_i.get('I', 0.0) for part_i in self.motions] + [0.0]
    self.all_j = [part_j.get('J', 0.0) for part_j in self.motions] + [0.0]
    self.all_r = [part_r.get('R', 0.0) for part_r in self.motions] + [0.0]
    """
    y_min = min(self.all_y) #0
    y_max = max(self.all_y) #30
    x_min = min(self.all_x) #0
    x_max = max(self.all_x) #20
    """
    ij_max = 2 * math.sqrt((max(self.all_i))**2 + (max(self.all_j))**2) #0
    d_max = 2 * (max(self.all_r)) 
    if ij_max >= d_max:
        self.dia_max = ij_max
    else: 
        self.dia_max = d_max
    
    extra = 10.0
    self.low_y = self.low_y - self.dia_max - extra
    self.high_y = self.high_y + self.dia_max + extra
    self.low_x = self.low_x - self.dia_max - extra
    self.high_x = self.high_x + self.dia_max + extra

    x_space = self.high_x - self.low_x
    y_space = self.high_y - self.low_y
    if x_space != y_space:
        if x_space > y_space: 
            max_space = x_space
            add_space = max_space - y_space
            self.low_y -= add_space/2
            self.high_y += add_space/2 # Phải gắn self vì hết lệnh if low_y... bị xóa bộ nhớ
        else: 
            max_space = y_space
            add_space = max_space - x_space
            self.low_x -= add_space/2
            self.high_x += add_space/2
    
    self.ax.set_xlim(self.low_x, self.high_x)
    self.ax.set_ylim(self.low_y, self.high_y)
    """
    # Test
    self.ax.set_xlim(-0.0005, 0.0005)
    self.ax.set_ylim(-0.0005, 0.0005)
    """
    #self.ax.set_xlim(min(all_x) - (2*(max(all_i) + max(all_j))) - 2, max(all_x) + (2*(max(all_i) + max(all_j))) - 2)
    #self.ax.set_ylim(min(all_y) - (2*(max(all_i) + max(all_j))) - 2, max(all_y) + (2*(max(all_i) + max(all_j))) - 2)
    
    self.run_button.config(state = tk.DISABLED)
    """
    self.stop_button.config(state = tk.NORMAL)
    self.pause_button.config(state = tk.NORMAL)
    """
    
    self.log_erase()
    self.log_bold("[SYSTEM] Start Simulation\n")
    
    self.simulation_line(0, 0.0, 0.0, 0.0, self.default_fr)