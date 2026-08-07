import tkinter as tk

def reset(self):
    if hasattr(self, 'serial') and self.serial is not None and self.serial.is_open:
        try:
            self.serial.write(b"reset\n")
            self.serial.flush()
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
        except Exception as e:
            print(f"Reset error: {e}")

    self.matlab_button.config(state = tk.DISABLED)

    self.log_erase()
    self.connected_mcu = False
    self.delivering_mcu = False
    self.run_button.config(state = tk.DISABLED)
    self.status_motor('X', 'gr')
    self.status_motor('Y', 'gr')
    self.status_motor('Z', 'gr')
    self.serial_gcode = []
    self.mcu_ack = False

    self.functions_stop()
    self.history_x, self.history_y, self.history_z = [0.0], [0.0], [0.0]
    self.travel_x, self.travel_y, self.travel_z = [0.0], [0.0], [0.0]
    self.velocity_x, self.velocity_y, self.velocity_z = [0.0], [0.0], [0.0]
    self.acceleration_x, self.acceleration_y, self.acceleration_z = [0.0], [0.0], [0.0]
    self.acce_j_x, self.acce_j_y, self.acce_j_z, = 0.0, 0.0, 0.0

    self.matlab_button.config(state = tk.DISABLED)
    self.test_elapsed = 0.0
    
    self.append_x = 0.0
    self.append_y = 0.0
    self.append_z = 0.0
    self.velocity_j = 0.0
    self.velocity_j_x = 0.0
    self.velocity_j_y = 0.0
    self.velocity_j_z = 0.0

    self.resolution_time = 0.0

    # Matlab
    self.matlab_x = [0.0]
    self.matlab_y = [0.0]
    self.matlab_z = [0.0]

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
    self.vector_x, self.vector_y = 0.0, 0.0

    # Reset ax lim
    self.all_x = [0.0]
    self.all_y = [0.0]
    self.all_i = [0.0]
    self.all_j = [0.0]
    self.all_r = [0.0]
    self.dia_max = 0.0
    self.low_y = 0.0
    self.high_y = 0.0
    self.low_x = 0.0
    self.high_x = 0.0
    
    self.curent_x = 0.0
    self.curent_y = 0.0
    self.curent_z = 0.0

    self.past_x = 0.0
    self.past_y = 0.0
    self.angle_velocity = 0.0

    #self.current_layer = 0
    self.last_z = None
    self.is_g91 = False
    #self.label.config(text = "Layer: --")
    
    self.status_motor("X", "gr")
    self.status_motor("Y", "gr")
    self.status_motor("Z", "gr")
    self.x_label.config(text = f"X: --.--- mm")
    self.y_label.config(text = f"Y: --.--- mm")
    self.z_label.config(text = f"Z: --.--- mm")

    self.feed_motion.set_data([], [])
    self.g0.set_data([], [])
    self.tool_head.set_data([0], [0])
    self.canvas.draw()
    self.log_text.delete("1.0", tk.END)
    self.log_bold("[SYSTEM] Reset successfully")

    self.serial_gcode = []