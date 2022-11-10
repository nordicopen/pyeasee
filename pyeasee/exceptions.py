class AuthorizationFailedException(Exception):
    pass


class NotFoundException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass


class ServerFailureException(Exception):
    pass


class ExceptionWithDict(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message.get("title", "")
        else:
            return f"{type(self).__name__} has been raised"


class ForbiddenServiceException(ExceptionWithDict):
    """Authenticated but access to resource not allowed."""


class BadRequestException(ExceptionWithDict):
    """Bad arguments or operation not allowed in this context."""
