import time
import threading

''' Put the logic for the timer here

'''

class Pomodoro:
    def start(self):
        self.running = True
        self.start_time = time.time() # Store precise start time
        self.current_time = 0
        # Modified this one line below into being several to enable multithreading
        # self.run_timer()
        timer_thread = threading.Thread(target=self.run_timer)
        timer_thread.daemon = True # Ensures thread stop when program exits
        timer_thread.start()

    def run_timer(self):
        # Updated to actually calculated elapsed time properly
        while self.running:
            elapsed_time = time.time() - self.start_time
            self.current_time = int(elapsed_time)

    def stop(self):
        self.running = False