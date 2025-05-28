from __future__ import annotations

from typing import TYPE_CHECKING, overload

from discord import Embed, utils

import disckit

if TYPE_CHECKING:
    from typing import Any, Optional

    import disckit.config


__all__ = ("MainEmbed", "ErrorEmbed", "SuccessEmbed")


class MainEmbed(Embed):
    """Represents a main embed for general use."""

    @overload
    def __init__(self, description: str, /, **kwargs: Any) -> None: ...

    @overload
    def __init__(
        self, title: str, description: str, /, **kwargs: Any
    ) -> None: ...

    @overload
    def __init__(self, *, title: str = ...) -> None: ...

    @overload
    def __init__(self, *, description: str = ...) -> None: ...

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the main embed.

        title: :class:`str`, default `None`
            The title of the main embed.
        """

        if description is None:
            description = title
            title = None

        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.MAIN_COLOR,
            timestamp=utils.utcnow(),
            **kwargs,
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )


class ErrorEmbed(Embed):
    """Represents an error embed."""

    @overload
    def __init__(self, description: str, /, **kwargs: Any) -> None: ...

    @overload
    def __init__(
        self, title: str, description: str, /, **kwargs: Any
    ) -> None: ...

    @overload
    def __init__(self, *, title: str = ...) -> None: ...

    @overload
    def __init__(self, *, description: str = ...) -> None: ...

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the main embed.

        title: :class:`str`, default `None`
            The title of the main embed.
        """

        if description is None:
            description = title
            title = None

        if title:
            title = f"{disckit.config.UtilConfig.ERROR_EMOJI} {title}"

        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.ERROR_COLOR,
            timestamp=utils.utcnow(),
            **kwargs,
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )


class SuccessEmbed(Embed):
    """Represents a success embed."""

    @overload
    def __init__(self, description: str, /, **kwargs: Any) -> None: ...

    @overload
    def __init__(
        self, title: str, description: str, /, **kwargs: Any
    ) -> None: ...

    @overload
    def __init__(self, *, title: str = ...) -> None: ...

    @overload
    def __init__(self, *, description: str = ...) -> None: ...

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the main embed.

        title: :class:`str`, default `None`
            The title of the main embed.
        """

        if description is None:
            description = title
            title = None

        if title:
            title = f"{disckit.config.UtilConfig.SUCCESS_EMOJI} {title}"

        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.SUCCESS_COLOR,
            timestamp=utils.utcnow(),
            **kwargs,
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )
