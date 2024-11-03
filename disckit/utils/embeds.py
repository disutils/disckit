from discord import Embed, utils
from typing import Optional, TYPE_CHECKING

import disckit

if TYPE_CHECKING:
    import disckit.config


class MainEmbed(Embed):
    """Represents a main embed for general use."""

    def __init__(self, description: Optional[str] = None, title: Optional[str] = None):
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the main embed.

        title: :class:`str`, default `None`
            The title of the main embed.
        """

        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.MAIN_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )


class SuccessEmbed(Embed):
    """Represents a success embed."""

    def __init__(self, description: Optional[str] = None, title: Optional[str] = None):
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the success embed.

        title: :class:`str`, default `None`
            The title of the success embed.
        """

        if title:
            title = f"{disckit.config.UtilConfig.SUCCESS_EMOJI} {title}"
        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.SUCCESS_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )


class ErrorEmbed(Embed):
    """Represents an error embed."""

    def __init__(self, description: Optional[str] = None, title: Optional[str] = None):
        """
        Parameters
        ----------
        description: :class:`str`
            The description of the error embed.

        title: :class:`str`, default `None`
            The title of the error embed.
        """

        if title:
            title = f"❌ {title}"
        super().__init__(
            title=title,
            description=description,
            color=disckit.config.UtilConfig.ERROR_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=disckit.config.UtilConfig.FOOTER_TEXT,
            icon_url=disckit.config.UtilConfig.FOOTER_IMAGE,
        )
