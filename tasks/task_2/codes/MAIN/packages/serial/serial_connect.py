import serial
from serial.tools import list_ports
import time
import tkinter as tk
import threading

def connect(self, log_boolean):
    try:
        self.connect_button.config(state = tk.DISABLED)
        if log_boolean:
            self.log_erase()
            self.log_bold("[SYSTEM] Connecting to MCU...\n")
        else:
            self.log_bold("         | Connecting to MCU...\n")

        port = str(self.port_com.get()).strip()
        if not port:
            self.log_erase()
            self.log_bold("[ERROR] Please check the Device Manager, and insert the correct\n        MCU port. Here are the available ports:\n\n")
            ports = list_ports.comports()
            for port in ports: self.log_position(f"        > {port}.\n")
            self.connect_button.config(state = tk.NORMAL)
            return

        if hasattr(self, 'serial') and self.serial is not None:
            if self.serial.is_open:
                self.serial.close()

        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = self.baudrate
        self.serial.timeout = 3
        self.serial.dtr = False
        self.serial.rts = False
        self.serial.open()
        time.sleep(2)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(b"PING\n")
        self.serial.flush()

        response = self.serial.readline().decode('utf-8', errors = 'ignore').strip()
        if response == "PONG":
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            if log_boolean:
                self.log_erase()
                self.log_bold(f"[SYSTEM] Successfully connected to MCU at {port}.\n")
                self.connected_mcu = True
            else:
                self.log_bold("         | Successfully connected to MCU.\n\n")
                self.connected_mcu = True
                listen_thread = threading.Thread(target = self.serial_listen, daemon = True)
                listen_thread.start()
            self.run_button.config(state=tk.NORMAL)
            
        else:
            self.serial.close()
            self.serial = None
            self.log_erase()
            self.log_bold(f"[ERROR] Failed to connect to MCU at {port}, received: \"{response}\".\n")
            self.connect_button.config(state=tk.NORMAL)
            return

    except serial.SerialException as e:
        if hasattr(self, 'serial') and self.serial is not None:
            if self.serial.is_open:
                self.serial.close()
            self.serial = None
        self.log_erase()
        self.log_bold(f"[ERROR] Unavailable {port} due to: \n{e}.\n")
        self.connect_button.config(state=tk.NORMAL)
    except Exception as e:
        if hasattr(self, 'serial') and self.serial is not None:
            if self.serial.is_open:
                self.serial.close()
            self.serial = None
        self.log_erase()
        self.log_bold(f"[ERROR] Unexpected error: \n{e}.\n")
        self.connect_button.config(state=tk.NORMAL)
