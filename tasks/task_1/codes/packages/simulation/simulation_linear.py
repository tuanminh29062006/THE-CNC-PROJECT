import math

def linear(self, index, ini_x, ini_y, ini_z,
            next_x, next_y, next_z, g_cmd,
            feed_rate, velocity,
            elapsed, distance, first_line):
        
    if not first_line and elapsed >= self.total_time:
        self.is_equal = False
        self.is_less = False
        self.is_greater = False
        self.line_x_done = False
        self.line_y_done = False
        self.line_z_done = False
        self.cos_x = 0.0
        self.cos_y = 0.0
        self.cos_z = 0.0
        #self.velocity_j = 0.0
        #self.velocity_j_x = 0.0
        #self.velocity_j_y = 0.0
        #self.velocity_j_z = 0.0
        self.t_acce, self.t_stable, self.t_dece, self.total_time = 0.0, 0.0, 0.0, 0.0
        self.vector_x, self.vector_y, self.vector_z = 0.0, 0.0, 0.0
        self.simulation_finalize(index, next_x, next_y, next_z,
                                 self.velocity_j_x, self.velocity_j_y, self.velocity_j_z,
                                 self.acce_j_x, self.acce_j_y, self.acce_j_z,
                                 feed_rate, g_cmd)
        return
    
    if first_line == True:
        self.line_x_done = False
        self.line_y_done = False
        self.line_z_done = False

        # Tính góc cos(alpha) cho mỗi trục
        self.cos_x = (next_x - ini_x) / distance
        self.cos_y = (next_y - ini_y) / distance
        self.cos_z = (next_z - ini_z) / distance

        self.append_x = ini_x
        self.append_y = ini_y
        self.append_z = ini_z

        """
        # Đã fix ở sim_line.py
        if not self.is_g91:
            self.start_x = ini_x
            self.start_y = ini_y
        """
        self.start_x = ini_x
        self.start_y = ini_y
        self.start_z = ini_z
        v_ini = 0.0
        v_end = 0.0
        v_stable = velocity 
        # Thời gian tăng tốc (acceleration):
        self.t_acce = (v_stable - v_ini) / self.acceleration
        # Quảng đường tăng tốc XY
        s_acce = (v_stable**2 - v_ini**2) / (2 * self.acceleration)

        # Thời gian giảm tốc (deceleration):
        self.t_dece = (v_end - v_stable) / self.deceleration
        # Quảng đường giảm tốc XY
        s_dece = (v_end**2 - v_stable**2) / (2 * self.deceleration)
        
        self.is_equal = False
        self.is_less = False
        self.is_greater = False

        if s_acce + s_dece == distance:
            self.is_equal = True
            self.total_time = self.t_acce + self.t_dece
        elif s_acce + s_dece < distance:
            self.is_less = True
            s_stable = distance - s_acce - s_dece
            self.t_stable = s_stable / v_stable
            self.total_time = self.t_acce + self.t_dece + self.t_stable
        else:
            self.is_greater = True
            v_absolute = math.sqrt((2 * (self.acceleration * self.deceleration * (-1)) * distance) / (self.acceleration - self.deceleration)) 
            self.t_acce = (v_absolute - v_ini) / self.acceleration
            self.t_dece = (v_end - v_absolute) / self.deceleration
            self.total_time = self.t_acce + self.t_dece
        
        if g_cmd == 1:
            dx = next_x - self.start_x
            dy = next_y - self.start_y
            dz = next_z - self.start_z
            self.vector_x = dx / distance
            self.vector_y = dy / distance
            self.vector_z = dz / distance
        
        first_line = False

    # elapse: là trôi qua, chỉ thời gian
    frame_dt = min(self.resolution_time, self.total_time - elapsed)

    # Trong mỗi khung hình, chia thành nhiều bước để tính toán mượt hơn
    sub_steptime = 0.001 # 1 ms
    steps = int(frame_dt/sub_steptime)
    # Kỹ tới mức nếu khoảng frame_dt quá nhỏ (nhỏ hơn 0.001 - sub_step_time)
    # Thì ít nhất cũng cho nó tính toán 1 lần luôn
    if steps < 1: steps = 1
    step_dt = frame_dt / steps

    # Với số step cần tính toán trong một frame
    for step in range(steps):
        if elapsed == 0: 
            velocity_i = 0.0
            velocity_i_x = 0.0
            velocity_i_y = 0.0
            velocity_i_z = 0.0
        else: 
            velocity_i = self.velocity_j
            velocity_i_x = self.velocity_j_x
            velocity_i_y = self.velocity_j_y
            velocity_i_z = self.velocity_j_z

        # Tính toán gia tốc theo thời điểm tức thời
        current_acce = 0.0
        current_acce_x = 0.0
        current_acce_y = 0.0
        current_acce_z = 0.0

        if self.is_equal or self.is_greater:
            if elapsed < self.t_acce:
                current_acce = self.acceleration
            else:
                current_acce = self.deceleration
        
        elif self.is_less:
            if elapsed < self.t_acce:
                current_acce = self.acceleration
            elif elapsed > self.t_acce and elapsed < ((self.t_acce + self.t_stable) - 0.00065):
                current_acce = 0.0
            #elif elapsed > int(self.t_acce + self.t_stable) and elapsed < self.total_time:
            else:
                current_acce = self.deceleration
        
        current_acce_x = current_acce * self.cos_x
        current_acce_y = current_acce * self.cos_y
        current_acce_z = current_acce * self.cos_z
        
        if g_cmd == 1:
            # s = v0.t + 1/2.a.t^2: length of distance (incremental method)
            step_distance = (velocity_i * step_dt) + (1/2) * current_acce * (step_dt**2)
            # v = v0 + at (incremental method)
            self.velocity_j = velocity_i + current_acce * step_dt

            self.append_x += step_distance * self.vector_x
            #self.velocity_j_x = math.sqrt((velocity_i_x**2) + 2 * current_acce_x * self.append_x)
            self.velocity_j_x = self.velocity_j * self.cos_x
            self.acce_j_x = (self.velocity_j_x - velocity_i_x) / step_dt

            self.append_y += step_distance * self.vector_y
            self.velocity_j_y = self.velocity_j * self.cos_y
            self.acce_j_y = (self.velocity_j_y - velocity_i_y) / step_dt

            self.append_z += step_distance * self.vector_z
            self.velocity_j_z = self.velocity_j * self.cos_z
            self.acce_j_z = (self.velocity_j_z - velocity_i_z) / step_dt
            
        elif g_cmd == 0:
            if not self.line_x_done or not self.line_y_done or not self.line_z_done: 
                if self.append_x != next_x:
                    step_distance_x = (velocity_i_x * step_dt) + (1/2) * current_acce_x * (step_dt**2)
                    self.velocity_j_x = velocity_i_x + current_acce_x * step_dt
                    self.append_x += step_distance_x
                    self.acce_j_x = (self.velocity_j_x - velocity_i_x) / step_dt
                    if self.append_x == next_x:
                        self.line_x_done = True
                        self.append_x = next_x
                
                if self.append_y != next_y:
                    step_distance_y = (velocity_i_y * step_dt) + (1/2) * current_acce_y * (step_dt**2)
                    self.velocity_j_y = velocity_i_y + current_acce_y * step_dt
                    self.append_y += step_distance_y
                    self.acce_j_y = (self.velocity_j_y - velocity_i_y) / step_dt
                    if self.append_y == next_y:
                        self.line_y_done = True
                        self.append_y = next_y
                
                if self.append_z != next_z:
                    step_distance_z = (velocity_i_z * step_dt) + (1/2) * current_acce_z * (step_dt**2)
                    self.velocity_j_z = velocity_i_z + current_acce_z * step_dt
                    self.append_z += step_distance_z
                    self.acce_j_z = (self.velocity_j_z - velocity_i_z) / step_dt
                    if self.append_z == next_z:
                        self.line_z_done = True
                        self.append_z = next_z
        
        if self.last_z != self.append_z:
            self.last_z = self.append_z
            self.z_label.config(text = f"Z-Height: {self.last_z:.2f} mm")

        self.history_append(self.append_x, self.append_y, self.append_z, self.velocity_j_x, self.velocity_j_y, self.velocity_j_z, self.acce_j_x, self.acce_j_y, self.acce_j_z,  g_cmd)
        
        #self.matlab_append(self.append_x, self.append_y, self.append_z)
        
        elapsed += step_dt
        self.matlab_append(elapsed, self.append_x)
        """
        # For test
        print(self.history_x)
        print(self.history_y)
        print(self.history_z)

        print(self.travel_x)
        print(self.travel_y)
        print(self.travel_z)
        """
    self.simulation_graphics(elapsed, g_cmd, index)
    self.simulation_loop(self.simulation_linear, index, self.append_x, self.append_y, self.append_z,
                                                next_x, next_y, next_z, g_cmd,
                                                feed_rate, velocity,
                                                elapsed, distance, first_line)