def update(self, line):
    parsed = self.serial_parse(line)

    if parsed is None:
        return
    
    self.status_coordinate(parsed['x'], parsed['y'], parsed['z'])
    self.history_append(parsed['x'], parsed['y'], parsed['z'], parsed['g'])
    self.matlab_append(parsed['step_x'], parsed['step_y'], parsed['step_z'])

    self.status_motor('X', 'o' if parsed['status_x'] == "run" else 'g')
    self.status_motor('Y', 'o' if parsed['status_y'] == "run" else 'g')
    self.status_motor('Z', 'o' if parsed['status_z'] == "run" else 'g')

    self.append_x = parsed['x']
    self.append_y = parsed['y']
    self.append_z = parsed['z']
    self.simulation_graphics()
    