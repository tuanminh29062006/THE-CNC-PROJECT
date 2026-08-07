import numpy as np
import math

def line(self, index, d_x, d_y, d_z, d_feed):
    if not self.is_running: return
    if index >= len(self.motions):
        self.log_bold("Done simulation ✔\n")
        self.functions_stop()
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
    """
    # For test:
    for id, line in enumerate(self.motions):
        print(f"{id}. {line}")
        if 'X' in line:
            incremental_x = line['X']
            self.current_x += incremental_x
            line['X'] = self.current_x
        print(f"\t Fixed: {id}. {line}")
    """
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
    
    """
    if line_c == 91:
        if 'X' in line:
            incremental_x = line['X']
            self.current_x += incremental_x
            line['X'] = self.current_x
        if 'Y' in line:
            incremental_y = line['Y']
            self.current_y += incremental_y
            line['Y'] = self.current_y
        if 'Z' in line:
            incremental_z = line['Z']
            self.current_z += incremental_z
            line['Z'] = self.current_z
    """
    # From here, every code within this file process in G90
    # Default: 
    """
    #Default values by calling in the end of start.py
    #d_x = 0.0
    #d_y = 0.0
    #d_z = 0.0
    #d_feed = 12000
    """
    line_g = line.get('G')
    line_x = line.get('X', d_x)
    line_y = line.get('Y', d_y)
    line_z = line.get('Z', d_z)
    #if 'F' in line:
    #    line_f = line['F']
    line_f = line['F'] if 'F' in line else d_feed
    
    """
    if line_z != d_z:
        self.last_z = line_z
        self.z_label.config(text = f"Z-Height: {self.last_z:.2f} mm")
    elif index == 0 and line_z == d_z:
        self.last_z = d_z
    """
    self.last_z = line_z
    self.z_label.config(text = f"Z-Height: {self.last_z:.2f} mm")

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
    # Ban đầu, chưa tính nội suy trục z
    # Khi line_x đã bằng d_x VÀ line_y = d_y VÀ line_z khác d_z: ta cho xử lí dòng tiếp theo
    if line_x == d_x and line_y == d_y and line_z != d_z:
        self.simulation_line(index + 1, line_x, line_y, line_z, line_f)
        return
    """

    # Phần dưới chỉ để animate
    g0_feedrate = 3000.0
    velocity = (g0_feedrate/60.0) if line_g == 0 else (line_f/60.0)

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
        # Nếu có distance từ A đến B, thì cho vẽ:
        self.simulation_linear(index, d_x, d_y, d_z, line_x, line_y, line_z, line_g,
                               line_f, velocity, 0.0, distance, True) 
        # Mới gọi, chưa chạy thì elapsed = 0.0 giây
    
    elif line_g in [2, 3, '02', '03']:
        if 'R' in line:
            line_r =  line['R']
            distance_d = math.sqrt((line_x - d_x)**2 + (line_y - d_y)**2)

            if distance_d == 0 or distance_d > (2 * abs(line_r)):
                self.simulation_line(index + 1, line_x, line_y, line_z, line_f)
                return
            
            middle_x = (line_x + d_x) / 2
            middle_y = (line_y + d_y) / 2
            distance_h = math.sqrt(line_r**2 - (distance_d/2)**2)

            is_ccw = (line_g == 3)
            is_over180 = (line_r < 0)

            if is_ccw ^ is_over180:
                # (G03 and <= 180) OR (G02 and > 180)
                origin_x = middle_x + (distance_h * ((d_y - line_y) / distance_d))
                origin_y = middle_y + (distance_h * ((line_x - d_x) / distance_d))
            else:
                # (G03 and > 180) OR (G02 and <= 180)
                origin_x = middle_x + (distance_h * ((line_y - d_y) / distance_d))
                origin_y = middle_y + (distance_h * ((d_x - line_y) / distance_d))
            
            line_r = abs(line_r)
        else:
            line_i = line.get('I', 0.0)
            line_j = line.get('J', 0.0)

            origin_x = d_x + line_i
            origin_y = d_y + line_j
            line_r = math.sqrt(line_i**2 + line_j**2)
            if line_r == 0:
                self.simulation_line(index + 1, line_x, line_y, line_z, line_f)
                return
        angle_start = math.atan2(d_y - origin_y, d_x - origin_x)
        angle_end = math.atan2(line_y - origin_y, line_x - origin_x)

        line_p = line.get('P', 1)
        if line_p < 1:
            line_p = 1

        if line_x == d_x and line_y == d_y:
            angle_rotation = (-2 * math.pi if line_g == 2 else 2 * math.pi) * line_p
        else:
            # Lúc này sẽ có một số trường hợp góc lớn:
            angle_rotation = angle_end - angle_start
            # Chấm một điểm bất kỳ ở mặt có trục y dương:
                # (G03) Khi vẽ một đường cong từ điểm đó đến một điểm (y dương) khác trong trục y dương:
                    # angle_rotation >0 (CCW), vẫn thể hiện được góc di chuyển
                # (G03) Khi vẽ một đường cong từ điểm đó (y dương) đến một điểm khác trong trục y âm:
                    # angle_rotation <0 (CW), KHÔNG ĐÚNG, đang đi theo chiều quay dương (CCW) mà -> SỬA:
            if line_g == 3 and angle_rotation < 0:
                # Sửa lại sao cho angle_rotation >0 (CCW)
                angle_rotation += 2 * math.pi

                # (G02) Khi vẽ một đường cong từ điểm đó (y dương) đến một điểm khác trong trục y dương:
                    # angle_rotation <0 (CW), vẫn thể hiện được góc di chuyển
                # (G02) Khi vẽ một đường cong từ điểm đó (y dương) đến một điểm khác trong trục y âm:
                    # angle_rotation <0 (CW), vẫn thể hiện được góc di chuyển
            
            # Chấm một điểm bất kỳ ở mặt có trục y âm:
                # (G03) Khi vẽ một đường cong từ điểm đó đến một điểm (y âm) khác trong trục y âm:
                    # angle_rotation >0 (CCW), vẫn thể hiện được góc di chuyển
                # (G03) Khi vẽ một đường cong từ điểm đó đến một điểm (y dương) trong trục y dương:
                    # angle_rotation >0 (CCW), vẫn thể hiện được góc di chuyển
                
                # (G02) Khi vẽ một đường cong từ điểm đó đến một điểm (y âm) khác trong trục y âm:
                    # angle_rotation <0 (CW), vẫn thể hiện được góc di chuyển
                # (G02) Khi vẽ một đường cong từ điểm đó đến một điểm (y dương) trong trục y dương:
                    # angle_rotation >0 (CCW), KHÔNG ĐÚNG, đang đi theo chiều quay âm (CW) mà -> SỬA:
            elif line_g == 2 and angle_rotation > 0:
                # Sửa lại sao cho angle_rotation <0 (CW)
                angle_rotation -= 2 * math.pi

            if line_p > 1:
                angle_rotation += ((-1) * (line_p - 1) * 2 * math.pi) if line_g == 2 else ((line_p - 1) * 2 * math.pi)

        angle_length = line_r * abs(angle_rotation)
        if angle_length == 0:
            self.simulation_line(index + 1, line_x, line_y, line_z, line_f)
            return

        self.simulation_arc(index, d_x, d_y, d_z,
                            line_x, line_y, line_z, line_g,
                            line_f, velocity,
                            0.0, angle_start,
                            angle_length, angle_rotation, 
                            origin_x, origin_y, line_r, True)