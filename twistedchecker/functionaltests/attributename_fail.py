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
        self.foo_bar_zar = None
        self.FooBarZar = None
        self.a = None
