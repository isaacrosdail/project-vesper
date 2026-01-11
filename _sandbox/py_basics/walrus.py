
# Assignment + condition in the same line
# Perfect for: avoiding duplicate expensive calls
# Cannot use it where assignment would be misleading/ambiguous (ex: as a standalone statement)
# Should NOT use it to hide mutation.

# The core rule is:
#  := only binds the value of an expression;
#  It does not exist to make side-effects more compact or to replace statements.
#  Anything that returns None (like list.append, dict.update, set.add) is therefore a dead end for walrus,
#  because rebinding would destroy your variable.

# FOR EXAMPLE: Here, this does not work.
def filter(self, strategy):
    # res = []
    for n in self.vals:
        if not strategy.removeValue(n):
            res := res.append(n)         # Mutating as we use the walrus operator = Python says NO.
    return res

# Pattern:
if (result := expensive_func()) is not None:
    ...


# Here, this gets parsed as:
# if (thing := (5 == 6)):
# So thing becomes False
# Whereas it looks like we're
if thing := 5 == 6:
    print("Not what you think")