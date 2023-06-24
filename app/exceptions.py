class AppException(Exception):
    """Base Exception"""

    @property
    def message(self) -> str:
        return "An application error occurred"


class ApplicationException(AppException):
    pass


class UnexpectedError(ApplicationException):
    pass


class RegisterHandlerError(ApplicationException):
    pass


class DaoError(UnexpectedError):
    pass
