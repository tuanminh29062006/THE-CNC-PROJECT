import math

def arc(self, index, ini_x, ini_y, ini_z,
        next_x, next_y, next_z, g_cmd,
        feed_rate, velocity,
        elapsed, arc_start,
        arc_length, arc_rotation, 
        ori_x, ori_y, radius, first_line):
    if not first_line and elapsed >= (self.total_time):
        # For Long Matlab:
        a = False
        if a:
            print(self.matlab_x)
            #print(self.matlab_y)
            #print(self.matlab_z)
        
        self.t_acce, self.t_stable, self.t_dece, self.total_time = 0.0, 0.0, 0.0, 0.0
        self.simulation_finalize(index, next_x, next_y, next_z,
                                 self.velocity_j_x, self.velocity_j_y, self.velocity_j_z,
                                 self.acce_j_x, self.acce_j_y, self.acce_j_z,
                                 feed_rate, g_cmd)
        return
    
    if first_line:
        self.past_x = ini_x
        self.past_y = ini_y
        self.angle_velocity = 0.0
        self.arc_next = arc_start

        self.append_x = ini_x
        self.append_y = ini_y
        self.append_z = ini_z

        v_ini = 0.0
        v_end = 0.0
        v_stable = velocity 
        # Thời gian tăng tốc (acceleration):
        self.t_acce = (v_stable - v_ini) / self.acceleration
        # Quảng đường tăng tốc XY
        s_acce = (v_stable**2 - v_ini**2) / (2 * self.acceleration)
        theta_acce = s_acce / radius

        # Thời gian giảm tốc (deceleration):
        self.t_dece = (v_end - v_stable) / self.deceleration
        # Quảng đường giảm tốc XY
        s_dece = (v_end**2 - v_stable**2) / (2 * self.deceleration)
        theta_dece = s_dece / radius

        theta_stable = abs(arc_rotation) - theta_acce - theta_dece
        
        self.is_equal = False
        self.is_less = False
        self.is_greater = False

        if theta_acce + theta_dece == abs(arc_rotation):
            self.is_equal = True
            self.total_time = self.t_acce + self.t_dece
        #elif theta_acce + theta_dece < abs(arc_rotation):
        elif theta_stable > 0:
            self.is_less = True
            self.t_stable = theta_stable / (v_stable / radius)
            self.total_time = self.t_acce + self.t_dece + self.t_stable
        elif theta_stable < 0:
            self.is_greater = True
            v_absolute = math.sqrt((2 * (self.acceleration * self.deceleration * (-1)) * arc_length) / (self.acceleration - self.deceleration)) 
            self.t_acce = (v_absolute - v_ini) / self.acceleration
            self.t_dece = (v_end - v_absolute) / self.deceleration
            self.total_time = self.t_acce + self.t_dece
        
        self.arc_unit_z = abs((next_z - ini_z) / arc_rotation)
        self.arc_increment_z = 0.0
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

    for step in range(steps):
        if elapsed == 0: 
            velocity_i = 0.0
            velocity_i_x = 0.0
            velocity_i_y = 0.0
            velocity_i_z = 0.0
            self.angular_vel_i = velocity_i / radius
        else: 
            self.angular_vel_i = self.angular_vel_j
            velocity_i = self.velocity_j
            velocity_i_x = self.velocity_j_x
            velocity_i_y = self.velocity_j_y
            velocity_i_z = self.velocity_j_z

            self.past_x = self.append_x
            self.past_y = self.append_y
        
        angular_acce = 0.0
        if self.is_equal or self.is_greater:
            if elapsed < self.t_acce:
                angular_acce = (self.acceleration / radius)
            else:
                angular_acce = (self.deceleration / radius)
        
        elif self.is_less:
            if elapsed < self.t_acce:
                angular_acce = (self.acceleration / radius)
            elif elapsed > self.t_acce and elapsed < ((self.t_acce + self.t_stable) - 0.00065):
                angular_acce = 0.0
            else:
                angular_acce = (self.deceleration / radius)

        step_angle = self.angular_vel_i * step_dt + (1/2) * angular_acce * (step_dt**2)
        if arc_rotation < 0: step_angle *= (-1)
        self.arc_next += step_angle
        self.arc_increment_z = abs(step_angle) * self.arc_unit_z
        self.angular_vel_j = self.angular_vel_i + angular_acce * step_dt
        self.velocity_j = self.angular_vel_j * radius
        
        self.append_x =  ori_x + (radius * math.cos(self.arc_next))
        self.append_y = ori_y + (radius * math.sin(self.arc_next))
        self.append_z += self.arc_increment_z if ((next_z - ini_z) > 0) else (-1 * self.arc_increment_z)


        self.angle_velocity = math.atan2(self.append_y - self.past_y, self.append_x - self.past_x)
        self.velocity_j_x = self.velocity_j * math.cos(self.angle_velocity)
        self.acce_j_x = (self.velocity_j_x - velocity_i_x) / step_dt

        self.velocity_j_y = self.velocity_j * math.sin(self.angle_velocity)
        self.acce_j_y = (self.velocity_j_y - velocity_i_y) / step_dt

        self.velocity_j_z = self.angular_vel_j * self.arc_unit_z
        if (next_z - ini_z < 0): self.velocity_j_z *= (-1)
        self.acce_j_z = (self.velocity_j_z - velocity_i_z) / step_dt

        if self.last_z != self.append_z:
            self.last_z = self.append_z
            self.z_label.config(text = f"Z-Height: {self.last_z:.2f} mm")

        self.history_append(self.append_x, self.append_y, self.append_z, self.velocity_j_x, self.velocity_j_y, self.velocity_j_z, self.acce_j_x, self.acce_j_y, self.acce_j_z, g_cmd)
        #self.matlab_append(round(self.append_x, 3), round(self.append_y, 3), round(self.append_z, 3))
        
        elapsed += step_dt

    self.simulation_graphics(elapsed, g_cmd, index)
    self.simulation_loop(self.simulation_arc, index, ini_x, ini_y, ini_z,
                                                next_x, next_y, next_z, g_cmd,
                                                feed_rate, velocity,
                                                elapsed, arc_start,
                                                arc_length, arc_rotation, 
                                                ori_x, ori_y, radius, first_line)