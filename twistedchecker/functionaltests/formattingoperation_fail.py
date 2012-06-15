# enable: W9301


num = 3
# we should use a tuple as the value
formatedString = "%d" % num

# a formatting operation using mapping value
# no warnings should be generated
mapFoo = {'num': 3}
formatedString = "%(num)d" % mapFoo
