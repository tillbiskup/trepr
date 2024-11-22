"""
Exceptions for the trepr package.

For preventing cyclic imports and for a better overview, all exception
classes of the trepr package are collected in this module. It is save for
every other module to import this module, as this module does *not* depend
on any other modules.

"""


class Error(Exception):
    """Base class for exceptions in this module."""


class DimensionError(Error):
    """Exception raised when the dimension of the data does not fit.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class RangeError(Error):
    """Exception raised when the given range is out of the dataset's range.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class UnitError(Error):
    """Exception raised when the unit does not fit.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message
