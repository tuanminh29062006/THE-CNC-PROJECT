#def graphics(self, a_x, append_y, append_z, velocity_j_x, velocity_j_y, velocity_j_z, elapsed):
def graphics(self, elapsed, g_cmd, index):
    self.tool_head.set_data([self.append_x], [self.append_y])
    self.feed_motion.set_data(self.history_x, self.history_y)
    self.g0.set_data(self.travel_x, self.travel_y)
    self.canvas.draw_idle()
    if elapsed > 0:
        self.log_position("\n")
        self.log_position(f"[t ={elapsed: 5.5f}s] X:{self.append_x: 5.5f} | Y:{self.append_y: 5.5f} | Z:{self.append_z: 5.5f}\n")
        self.log_position(f"Vx:{self.velocity_j_x: 5.5f} | Vy:{self.velocity_j_y: 5.5f} | Vz:{self.velocity_j_z: 5.5f} | G:{g_cmd} | Line:{index}\n")
        self.log_position(f"Ax:{self.acce_j_x: 5.5f} | Ay:{self.acce_j_y: 5.5f} | Az:{self.acce_j_z: 5.5f}\n")