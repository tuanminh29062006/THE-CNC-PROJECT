def coordinate(self, x, y, z):
    self.x_label.config(text = f"X: {x: 8.3f} mm")
    self.y_label.config(text = f"Y: {y: 8.3f} mm")
    self.z_label.config(text = f"Z: {z: 8.3f} mm")