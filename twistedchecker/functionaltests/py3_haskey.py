# enable: W9602

# an example of call has_key on a dict
# a warning should be generated

if {}.has_key("bar"):
    pass

foo = {}

if foo.has_key("bar"):
    pass

# an example of call has_key on a existing class
# no warnings should be showed in this case
from twisted.python.util import InsensitiveDict

bar = InsensitiveDict()
if bar.has_key("bar"):
    pass

# an example of call has_key on a unknown object
# no warnings should be showed as we do not know what it is

result = baz.has_key("bar")
