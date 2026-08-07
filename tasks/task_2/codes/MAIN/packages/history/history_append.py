#def append(self, append_x, append_y, append_z, velocity_j_x, velocity_j_y, velocity_j_z, acce_j_x, acce_j_y, acce_j_z, g_cmd):
def append(self, append_x, append_y, append_z, g_cmd):
    if g_cmd == 0:
        self.travel_x.append(append_x)
        self.travel_y.append(append_y)
        self.travel_z.append(append_z)
    else:
        self.history_x.append(append_x)
        self.history_y.append(append_y)
        self.history_z.append(append_z)
    """
    self.velocity_x.append(velocity_j_x)
    self.velocity_y.append(velocity_j_y)
    self.velocity_z.append(velocity_j_z)

    self.acceleration_x.append(acce_j_x)
    self.acceleration_y.append(acce_j_y)
    self.acceleration_z.append(acce_j_z)
    """
    
    



