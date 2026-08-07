import time

def receive(self, deliver):
    count_gcode = len(deliver)
    self.log_bold(f"         | Start delivering {count_gcode} lines.\n\n")

    for index, line in enumerate(deliver):
        if hasattr(self, "delivering_mcu") and not self.delivering_mcu:
            break
        gcode_line = line.strip()
        if not gcode_line: continue

        self.mcu_ack = False
        self.serial.write((line + '\n').encode('utf-8'))
        self.serial.flush()

        start_time = time.time()
        while not self.mcu_ack:
            if time.time() - start_time > 5.0:
                self.log_bold(f"\n[ERROR] Serial timeout at line {index + 1}.\n")
                self.delivering_mcu = False
                return
            time.sleep(0.002)

    self.log_bold(f"\n         | Finish delivering {count_gcode} lines.\n")
    self.delivering_mcu = False