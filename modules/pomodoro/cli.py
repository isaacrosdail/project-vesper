from pomodoro import Pomodoro
import time

''' Here we handle the user inputs (CLI/text) for the timer


'''

def cli(pomodoro):
    command = input()

    match command:
        case "start":
            print("Timer started!")
            pomodoro.start()
            while pomodoro.running:
                print(pomodoro.currentTime)
                time.sleep(1)

        case "stop":
            pomodoro.stop()
            print("Timer stopped!")

        # Default case
        case _:
            return "Please enter start or stop"

# Main lives here for now
def main():
    pomodoro = Pomodoro() # Create pomodoro variable/object, storing instance of Pomdoro class?
    cli(pomodoro) # Start user input handling

if __name__== "__main__":
    main()