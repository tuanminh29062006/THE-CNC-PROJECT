def m_code(self):
    print("\n")
    print("~~~ YOUR MATLAB CODE IS READY TO COPY  ~~~\n")
    #print(f"x = {self.matlab_x};\ny = {self.matlab_y};\nz = {self.matlab_z};\nfigure;\nplot3(x, y, z, '-o', 'LineWidth', 1, 'MarkerSize', 6, 'MarkerFaceColor', 'blue');\nxlabel('x-axis');\nylabel('y-axis');\nzlabel('z-axis');\ngrid on;\ntitle('3D G-Code Plot');\nview(3);\n")
    print(f"x = {self.matlab_x};\ny = {self.matlab_y}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("\n")

    self.log_position("\n")
    self.log_bold("[SYSTEM] ")
    self.log_position("Matlab Code is Ready\n")
    self.log_position(">> Open Terminal to Copy\n")