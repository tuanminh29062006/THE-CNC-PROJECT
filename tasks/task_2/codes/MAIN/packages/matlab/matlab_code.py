def m_code(self):
    print("\n")
    print("~~~ YOUR MATLAB CODE IS READY TO COPY  ~~~\n")
    print(
    f"x = {self.matlab_x};\n"
    f"y = {self.matlab_y};\n"
    f"z = {self.matlab_z};\n"
    f"dt = {self.resolution_time};\n"
    f"t = (0:length(x)-1) * dt;\n\n"
    f"figure;\n"
    f"plot(t, x, '-o', 'LineWidth', 1.5, 'MarkerSize', 4, 'DisplayName', 'X-Axis Pulses');\n"
    f"hold on;\n"
    f"plot(t, y, '-s', 'LineWidth', 1.5, 'MarkerSize', 4, 'DisplayName', 'Y-Axis Pulses');\n"
    f"plot(t, z, '-^', 'LineWidth', 1.5, 'MarkerSize', 4, 'DisplayName', 'Z-Axis Pulses');\n"
    f"hold off;\n\n"
    f"xlabel('Second');\n"
    f"ylabel('Pulse');\n"
    f"title('Stepper Motor Pulse');\n"
    f"legend('Location', 'northeast');\n"
    f"grid on;\n")

    #print(f"x = {self.matlab_x};\n\n\ny = {self.matlab_y};")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("\n")

    self.log_position("\n")
    self.log_bold("[SYSTEM] ")
    self.log_position("Matlab Code is Ready\n")
    self.log_position(">> Open Terminal to Copy\n")