
## rsplit and rpartition (differences?)

thing = "todd/the/god/howard"

thing_two = thing.rsplit('/', 1)
thing_three = thing.rpartition("/")
print(thing_two)
print(thing_three)



# join

# The string whose method is called is inserted in between each given string.
# The result is returned as a new string.
# Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'