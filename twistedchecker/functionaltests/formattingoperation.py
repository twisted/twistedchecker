# enable: W9501


num = 3
# we should use a tuple as the value
formattedString = "%d" % num

formattedString = "%d" % (num)

# a formatting operation using mapping value
# no warnings should be generated
mapFoo = {'num': 3}
formattedString = "%(num)d" % mapFoo

num = 3
# a tuple used in the string formatting operation.
formattedString = "%d" % (num,)
