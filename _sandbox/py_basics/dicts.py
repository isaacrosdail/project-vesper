
my_tuple = ('aX', 'bY', 'cZ')
converted = dict(my_tuple)

# becomes
#my_dict = {'a': 'X', 'b': 'Y', 'c': 'Z'}

print(converted)



#### ALSO:

# MERGE OPERATOR - Use cases?
# data = completion.to_api_dict() | {"progress": progress} # | merge operator to tack onto dict