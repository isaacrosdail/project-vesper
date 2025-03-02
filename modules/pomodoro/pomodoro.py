import time
import threading

''' Put the logic for the timer here

'''

class Pomodoro:
    def start(self):
        self.running = True
        self.currentTime = 0
        # Modified this one line below into being several to enable multithreading
        # self.run_timer()
        timer_thread = threading.Thread(target=self.run_timer)
        timer_thread.daemon = True # Ensures thread stop when program exits
        timer_thread.start()

    def run_timer(self):
        while self.running:
            self.currentTime += 1
            time.sleep(1)

    def stop(self):
        self.running = False