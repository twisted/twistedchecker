# enable: C0103

class FooClass:
    """
    Attribute names should be in mixed case,
    with the first letter lower case,
    each word separated by having its first letter capitalized
    just like method names.
    And all private names should begin with an underscore.
    """

    def __init__(self):
        """
        A init of this class
        """
        self.fooBarZar = None
        self._fooBarZar = None
        self.foobar = None
        # In some cases constants are lazy initialized as instance members.
        self.FOOBARZAR = None
