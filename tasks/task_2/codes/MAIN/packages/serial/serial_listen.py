import time
import tkinter as tk

def listen(self):
    # Luôn chạy sau connect_mcu, nên không lo PONG
    while hasattr(self, "connected_mcu") and self.connected_mcu:
        try:
            if hasattr(self, "serial") and self.serial is not None and self.serial.is_open:
                serial_response = self.serial.readline()
                if serial_response:
                    response = serial_response.decode('utf-8', errors = 'ignore').strip()
                    if response.startswith("<POS"):
                        self.root.after(0, self.serial_update, response)
                    elif response == "received_t":
                        self.log_bold(f"         | Received Resolution Time.\n")
                        self.mcu_ack = True
                    elif response == "received":
                        self.log_bold(f"         | Received G-Code line.\n")
                        self.mcu_ack = True
                    elif response == "finish":
                        self.reset_button.config(state = tk.NORMAL)
                        self.matlab_button.config(state = tk.NORMAL)
                    elif response:
                        self.reset_button.config(state = tk.NORMAL)
                        self.log_bold(f"\n[ERROR] Unwanted response: {response}.\n")
            #time.sleep(0.001)

        except Exception as e:
            self.log_bold(f"[ERROR] Listen thread got error: {e}.\n")
            break