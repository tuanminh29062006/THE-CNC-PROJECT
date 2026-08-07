def ser_parse(self, line):
    match = self.parse_pattern_serial.search(line)
    
    if not match:
        return None

    try:
        return {
            "g": int(match.group("g")),
            "x": float(match.group("x")),
            "y": float(match.group("y")),
            "z": float(match.group("z")),
            "status_x": match.group("status_x").strip().lower(), 
            "status_y": match.group("status_y").strip().lower(),
            "status_z": match.group("status_z").strip().lower(),
            "step_x": float(match.group("step_x")),
            "step_y": float(match.group("step_y")),
            "step_z": float(match.group("step_z"))
        }
            
    except ValueError:
        print("error")
        return None