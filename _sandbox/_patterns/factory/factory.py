# Factory Pattern
# A type of Creational Pattern

# NOTE: "What's the diff between this and the Builder pattern tho?"
# The diff is about when and how the object in assembled.
# Factory: Creates fully-formed objects in one step by selecting a pre-defined variant (cheeseburger, vegan, deluxe),
#           so the caller just asks for a type and gets a finished product.
# FOR: Choosing between known recipes.

# Builder: For assembling something when the recipe itself is dynamic or multi-stage. If your
# object has many combinations, conditonal steps, or needs validation before it's "done",
# Builder fits better.

class Burger:
    def __init__(self, ingredients):
        self.ingredients = ingredients

    def print(self):
        print(self.ingredients)


class BurgerFactory:

    def createCheeseBurger(self):
        ingredients = ["bun", "cheese", "beef-patty"]
        return Burger(ingredients)

    def createDeluxeCheeseBurger(self):
        ingredients = ["bun", "tomatoe", "lettuce", "cheese", "beef-patty"]
        return Burger(ingredients)

    def createVeganBurger(self):
        ingredients = ["bun", "special-sauce", "veggie-patty"]
        return Burger(ingredients)
