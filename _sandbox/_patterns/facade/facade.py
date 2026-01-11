# Facade Pattern
# A type of Structural Pattern

# This one is as obvious as it feels lol. Don't overthink it.
# Just write good function interfaces with clear, coherent/sensible contracts.

# "Facade is just encapsulation": Facade pattern is kinda just the formal name for
# what good encapsulation already does - hide messy internals behind a clean interface. The facade IS encapsulation, you're just
# encapsulating a whole subsystem instead of just one class.

# "one of the reasons i love return types is that you can actually facade it"?
# This is about type safety making facades more powerful? With strong typing, your
# facade can return a clean, typed result while hiding all the gnarly internal types:
def get_user_dashboard() -> UserDashboard:
    # Internally: hit 5 different APIs, parse XML, 
    # join data, handle errors, cache results...
    # Client just gets the clean type they expect
    return UserDashboard(...)
# The return type becomes your 'contract' - clients know exactly what they're getting, but have
# no idea (and don't care) about the 47 internal classes you just used to build it.