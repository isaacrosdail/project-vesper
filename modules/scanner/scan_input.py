# Shared scanner logic here?
## Idea: use evdev on Pi (unfortunately evdev is Linux-only supported via /dev/input/event)

''' Check OS type to determine whether to use real scan loop (Pi/Linux) or simulate scan loop (Windows)
from sys import platform

if platform == "linux":
    real_scan_loop()
elif platform == "win32":
    simulate_scan_loop(callback)

'''

def simulate_scan_loop(callback):
    while True:
        fake = input("Simulate barcode: ")
        callback(fake)