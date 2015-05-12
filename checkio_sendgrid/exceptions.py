# -*- coding: utf-8 -*-


class SendgridError(StandardError):
    """ Base error. """
    def __init__(self, message, result=None):
        super(SendgridError, self).__init__(message)
        self.result = result


class AuthenticationError(SendgridError):
    """ Raised when a request cannot be authenticated by the API. """
    pass


class FormatNotAllowed(SendgridError):
    """ Raised when the API returns an error other than an auth or not found. """
    pass


class ResourceNotFound(SendgridError):
    """ Raised when a resource cannot be found e.g. a non-existant User. """
    pass


class ServerError(SendgridError):
    """ Raised when the API returns an error other than an auth or not found. """
    pass
