# Found regarding this question:
# https://stackoverflow.com/questions/13184275/how-to-retrieve-python-list-of-sqlalchemy-result-set


# Posted by zzzeek, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-03, License - CC BY-SA 3.0
result = [("idk"), ("just"), ("an"), ("example")]

# result = [r[0] for r in result]
#  VS.
# result = [r for r, in result] # for dealing with discrete columns? idk
