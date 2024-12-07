from disckit.config import CogEnum


class DisException(Exception):
    """Base class of disckit's exceptions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class CogLoadError(DisException):
    """Raised when loading a cog fails.

    Attributes
    ------------
    cog: :class:`CogEnum`
        The cog that failed loading.
    """

    def __init__(self, message: str, cog: CogEnum, **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.cog = cog


class LemmaLoadError(DisException):
    """Raised when an error occurs in loading the translator

    Attributes
    ------------
    error_code: :class:`int`
        The error code of the exception.
    """

    def __init__(self, message: str, error_code: int, **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.error_code = error_code
