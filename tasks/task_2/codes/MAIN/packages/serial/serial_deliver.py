import threading

def deliver(self):
    if hasattr(self, "delivering_mcu") and self.delivering_mcu:
        self.log_bold("[ERROR] MCU is already processing.\n")
        return
    if not hasattr(self, "serial_gcode") and not self.serial_gcode:
        self.log_bold("[ERROR] G-Code is empty.\n")
        return
    
    self.log_bold("         | Checking MCU Connection...\n")
    self.serial_connect(False)

    if hasattr(self, "connected_mcu") and self.connected_mcu:
        self.log_bold("         | Ready to deliver.\n")
        self.delivering_mcu = True
        gcode_copy = list(self.serial_gcode)
        thread = threading.Thread(target = self.serial_receive, args = (gcode_copy,))
        thread.daemon = True
        thread.start()
    else:
        return