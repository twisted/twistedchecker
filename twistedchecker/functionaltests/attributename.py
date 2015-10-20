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
        # Bad names.
        self.foo_bar_zar = None
        self.FooBarZar = None
        self.a = None
        self._fooBar_ = None
        self._fooBar__ = None
        self.__fooBar_ = None
        self.___longStart__ = None
        self.__longEnd___ = None

        # Good names.
        self.fooBarZar = None
        self._fooBarZar = None
        self.foobar = None
        # Any __*__ name is accepted.
        self.__foobar__ = None
        self.__fooBar__ = None
        self.__foo_bar__ = None
        self.__dict__ = {}
        self.__version__ = {}
        self.__a__ = {}
        # In some cases constants are lazy initialized as instance members.
        self.FOOBARZAR = None
