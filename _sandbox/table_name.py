import regex

def try_me(input: str):
    # CamelCase → snake_case first
    name = regex.sub('([a-z0-9])([A-Z])', r'\1_\2', input).lower()

    # Pluralize
    if name.endswith('y') and name[-2] not in 'aeiou':
        return name[:-1] + 'ies'  # entry → entries, daily_entry → daily_entries
    else:
        return name + 's'  # task → tasks, boy → boys
    

mything = ['DailyEntry', 'TimeEntry', 'Product', 'Task']

for thing in mything:
    print(try_me(thing))