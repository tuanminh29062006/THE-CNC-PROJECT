def finalize(self, index, n_x, n_y, n_z, vel_j_x, vel_j_y, vel_j_z, acce_j_x, acce_j_y, acce_j_z, n_feed, g_cmd):
    self.history_append(n_x, n_y, n_z, vel_j_x, vel_j_y, vel_j_z, acce_j_x, acce_j_y, acce_j_z, g_cmd)
    self.simulation_graphics(0.0, g_cmd, index)
    self.simulation_line(index + 1, n_x, n_y, n_z, n_feed)