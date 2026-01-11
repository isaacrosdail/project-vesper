# Singleton Pattern: "There can only be one."
# A type of Creational Pattern
# Singley great for: Shared source of truth.

# "sucks until it's really awesome" 
# Global mutable state creates hidden coupling, makes tests order-dependent, and turns
# change into cross-cutting risk.
# Granted, when you WANT this behavior, you REALLY want it.

class ApplicationState:
    instance = None

    def __init__(self):
        self.isLoggedIn = False

    @staticmethod
    def getAppState():
        if not ApplicationState.instance:
            ApplicationState.instance = ApplicationState()
        return ApplicationState.instance

# For the first time, logged in val is initially false
appState1 = ApplicationState.getAppState()
print(appState1.isLoggedIn) # False

appState2 = ApplicationState.getAppState()
appState1.isLoggedIn = True

print(appState1.isLoggedIn) # True
print(appState2.isLoggedIn) # True