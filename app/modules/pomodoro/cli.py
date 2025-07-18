import time

from pomodoro import Pomodoro

''' Here we handle the user inputs (CLI/text) for the timer


'''

def cli(pomodoro):

    while True:
        command = input()

        match command:
            case "start":
                print("Timer started!")
                pomodoro.start()
            case "stop":
                pomodoro.stop()
                print("Timer stopped!")
            # Default case
            case _:
                return "Please enter start or stop"

        while pomodoro.running:
            print(pomodoro.current_time)
            time.sleep(1)

# Main lives here for now
def main():
    pomodoro = Pomodoro() # Create pomodoro variable/object, storing instance of Pomdoro class?
    cli(pomodoro) # Start user input handling

if __name__== "__main__":
    main()