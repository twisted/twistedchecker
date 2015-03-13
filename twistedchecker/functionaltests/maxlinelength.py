# enable: C0301
# max line length of Twsited projects should be 79
print "this line is long long  long  long long long long long ends at column 80"

# But comments with url should be excepted.
# http://thisurlisverylongandwillneverfitinto80columnsnomatterwhat.example.com/somegreatcontent.tml

""""
Long url form docstrings are ignored.
See U{https://thisurlisverylongandwillneverfitinto80columnsnomatterwhat.example.com/somegreatcontent.html}
"""
