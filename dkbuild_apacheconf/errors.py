class DkbuileApacheError(Exception):
    """Base class for our exceptions.
    """


class NoServerIniError(DkbuileApacheError):
    """No server.ini file was found.
    """
