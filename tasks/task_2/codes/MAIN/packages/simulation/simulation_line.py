import numpy as np
import math

def line(self, index, d_x, d_y, d_z, d_feed):
    if not self.is_running: return
    if index >= len(self.motions):
        self.log_bold("         | Gcode Parsed.\n\n")
        self.serial_deliver()
        return
    
    line = self.motions[index]
    line_c = line.get('C')

    if index == 0:
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        
    if line_c == 90 or line_c == 91:
            if 'X' not in line and 'Y' not in line and 'Z' not in line:
                self.simulation_line(index + 1, d_x, d_y, d_z, d_feed)
                return
   
    if line_c == 91:
        if 'X' in line:
            incremental_x = line['X']
            line['X'] = self.current_x + incremental_x
            self.current_x = line['X']
        if 'Y' in line:
            incremental_y = line['Y']
            line['Y'] = self.current_y + incremental_y
            self.current_y = line['Y']
        if 'Z' in line:
            incremental_z = line['Z']
            line['Z'] = self.current_z + incremental_z
            self.current_z = line['Z']
    elif line_c == 90:
        if 'X' in line:
            self.current_x = line['X']
        if 'Y' in line:
            self.current_y = line['Y']
        if 'Z' in line:
            self.current_z = line['Z']
    
    line_g = line.get('G')
    line_x = line.get('X', d_x)
    line_y = line.get('Y', d_y)
    line_z = line.get('Z', d_z)

    if line_g == 0:
        line_f = self.default_fr_g0
    else:
        line_f = line['F'] if 'F' in line else d_feed

    """
    self.last_z = line_z
    self.z_label.config(text = f"Z: {self.last_z:.2f} mm")
    """

    """
    # Khi nhập lệnh line, cái d_x, d_y, d_z là tọa độ ban đầu (điểm A)
    if line_g == 0:
        if not np.isnan(self.history_x[-1]): # Cái ký tự trước đó trong list
            self.history_x.append(np.nan) # np.nan nâng bút không vẽ
            self.history_y.append(np.nan)
            self.history_z.append(np.nan)
    else:
        # Ở file sim_line.py này, chỉ thêm các tọa độ ban đầu (điểm A) của mỗi dòng lệnh
        # ở file sim_linear.py mới chia nhỏ step ra nội suy tọa độ để đến được điểm B
        if np.isnan(self.history_x[-1]):
            self.history_x.append(d_x) # thêm vào lịch sử tọa độ x di chuyển ở vị trí ban đầu ngay khi gọi lệnh
                                       # lúc chưa xử lí
            self.history_y.append(d_y)
            self.history_z.append(d_z)
    """

    if line_g in [90, 91]:
        self.simulation_line(index + 1, line_x, line_y, line_z, line_f)
        return

    if line_g in [0, 1]:
        # A (x = d_x; y = d_y)  ->  B (x = t_x; y = t_y)
        # Distance AB = math.sqrt((xB - xA)^2 + (yB - yA)^2)
        distance = math.sqrt((line_x - d_x)**2 + (line_y - d_y)**2 + (line_z - d_z)**2)
        if distance == 0: # Tránh trường hợp mà line_z = d_z trùng hết tọa độ cũ
            self.simulation_line(index + 1, line_x, line_y, line_z, line_f) # Xử lí dòng tiếp theo khi độ dài line vẽ = 0
            return
        line = f"G{line_g} X{line_x:.5f} Y{line_y:.5f} Z{line_z:.5f} F{line_f:.5f}"
        self.serial_gcode.append(line)
        self.simulation_line(index + 1, line_x, line_y, line_z, line_f)