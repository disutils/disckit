from __future__ import annotations

from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from typing import Any

    from disckit.config import CogEnum


class DisException(Exception):
    """Base class of disckit's exceptions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PaginatorError(DisException):
    """Base exception of all paginator errors."""


@final
class CogLoadError(DisException):
    """Raised when loading a cog fails.

    Attributes
    ------------
    cog: :class:`CogEnum`
        The cog that failed loading.
    """

    def __init__(self, message: str, cog: CogEnum, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.cog = cog


@final
class PaginatorInvalidPages(PaginatorError):
    """Raised when an invalid amount of pages are supplied to the paginator."""


@final
class PaginatorInvalidCurrentPage(PaginatorError):
    """Raised when the current page is invalid of a paginator."""


@final
class PaginatorNoHomePage(PaginatorError):
    """Raised when no page is supplied."""
