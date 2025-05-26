import time
from datetime import datetime, timedelta

# 60-minute "work block" timer
# Within this, we'll have the following:
# At 50 mins elapsed -> break time
# At every 20 mins elapsed -> eye/movement break for 20 secs
def run_work_block():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=60)
    eye_breaks = {
        "eye1": start_time + timedelta(minutes=20),
        "eye2": start_time + timedelta(minutes=20)
    }
    # Dictionary comprehension
    # For every "thing" in the dict eye_breaks, we'll do: "thing1": False, and so on
    fired = {k: False for k in eye_breaks}
    break_started = False

    # Duration of entire work block
    while datetime.now() < end_time:
        
        # Eye Break 1
        if not fired["eye1"] and datetime.now() >= eye_breaks["eye1"]:
            ## TRIGGERS SOUNDS / UI / ETC ON THIS LINE
            time.sleep(20)
            fired["eye1"] = True
        # Eye Break 2
        if not fired["eye2"] and datetime.now() >= eye_breaks["eye2"]:
            ## TRIGGERS SOUNDS / UI / ETC ON THIS LINE
            time.sleep(20)
            fired["eye2"] = True
        
        # Work Over -> Start 10-min break
        if not break_started and datetime.now() >= start_time + timedelta(minutes=50):
            ## TRIGGERS SOUNDS / UI / ETC ON THIS LINE
            break_started = True
            break_started_time = datetime.now() # For optional countdown
        
        # Avoid hammering CPU (otherwise we'd run all our loop logic every microsecond)
        time.sleep(1)