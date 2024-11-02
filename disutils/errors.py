from disutils.config import CogEnum


class DisException(Exception):
    """Base class of disutils exceptions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class CogLoadError(DisException):
    """Raised when loading a cog fails.

    Attributes
    ------------
    cog: :class:`CogEnum`
        The cog that failed loading.
    """

    def __init__(self, message: str, cog: CogEnum) -> None:
        super().__init__(message)
        self.cog = cog
