def motor(self, axis, color, outline):
    """
    Ví dụ:
    set_axis_status('X', 'g')  # Xanh lá (Đang chạy/Đã Home)
    set_axis_status('Y', 'o')  # Cam (Cảnh báo/Lỗi)
    set_axis_status('Z', 'gr')  # Xám (Idle/Disconnect)
    """
    if color == "g":
        color = "#2ecc71"
    elif color == "o":
        color = "#FFA500"
    else:
        color = "#7f8c8d"

    axis = axis.upper()
    if axis == "X":
        self.canvas_x.itemconfig(self.square_x, fill = color, outline = outline)
    elif axis == "Y":
        self.canvas_y.itemconfig(self.square_y, fill = color, outline = outline)
    if axis == "Z":
        self.canvas_z.itemconfig(self.square_z, fill = color, outline = outline)