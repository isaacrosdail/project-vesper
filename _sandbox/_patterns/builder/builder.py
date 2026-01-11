# Builder Pattern
# A type of Creational Pattern

# NOTE: "What's the diff between this and the Builder pattern tho?"
# The diff is about when and how the object in assembled.
# Factory: Creates fully-formed objects in one step by selecting a pre-defined variant (cheeseburger, vegan, deluxe),
#           so the caller just asks for a type and gets a finished product.
# FOR: Choosing between known recipes.

# Builder: For assembling something when the recipe itself is dynamic or multi-stage. If your
# object has many combinations, conditonal steps, or needs validation before it's "done",
# Builder fits better.

# We don't immediately have to pass in all the parameters.
# Primeagean: "You should always use a builder pattern [over a factory pattern]"

class Burger:
    def __init__(self):
        self.buns = None
        self.patty = None
        self.cheese = None

    def setBuns(self, bunStyle):
        self.buns = bunStyle

    def setPatty(self, pattyStyle):
        self.patty = pattyStyle

    def setCheese(self, cheeseStyle):
        self.cheese = cheeseStyle


class BurgerBuilder:
    def __init__(self):
        self.burger = Burger()

    def addBuns(self, bunStyle):
        self.burger.setBuns(bunStyle)
        return self

    def addPatty(self, pattyStyle):
        self.burger.setPatty(pattyStyle)
        return self

    def addCheese(self, cheeseStyle):
        self.burger.setCheese(cheeseStyle)
        return self

    def build(self):
        return self.burger

# Instantiate the BurgerBuilder
# Add the buns/cheese/patty we want
# NOTE: We can chain these, because each one returns a reference to the builder!
burger = BurgerBuilder() \
    .addBuns("sesame") \
    .addPatty("fish-patty") \
    .addCheese("swiss cheese") \
    .build()

#### ALSO: When you study this next, me, "protobuffs are amazing" was mentioned, so we should try a form of those. Means "Protocol Buffers".
# ChatGPT's comment about them, to study:
# generate objects that often have many optional fields, defaults, and versioned schema rules, which makes direct construction messy.
# A builder lets you set fields step-by-step while enforcing ordering, validation, or required # # combinations before producing the final message. 
# This is especially useful when messages are assembled from multiple sources, transformations, or conditional logic. 
# Instead of sprinkling field assignments across your code, you #centralize “how a valid message is built” in one place. 
# That keeps your serialization layer strict while letting the rest of the system stay clean.