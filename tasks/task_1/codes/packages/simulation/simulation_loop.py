def loop(self, callback_function, *args):
    if not self.is_running: return
    if self.is_paused:
        # (usually for window).after(time to wait in ms, lambda: function to process)
        self.root.after(200, lambda: self.simulation_loop(callback_function, *args))
        return
    self.root.after(int(self.resolution_time * 1000), lambda: callback_function(*args))
