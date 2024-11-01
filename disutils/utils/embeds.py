from discord import Embed, utils
from typing import Optional

from disutils.config import UtilConfig


class MainEmbed(Embed):
    """Represents a main embed with a title, description, and other properties."""

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
            color=UtilConfig.MAIN_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=UtilConfig.FOOTER_TEXT,
            icon_url=UtilConfig.AVATAR_URL,
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
            title = f"{UtilConfig.GREEN_CHECK} {title}"
        super().__init__(
            title=title,
            description=description,
            color=UtilConfig.SUCCESS_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=UtilConfig.FOOTER_TEXT,
            icon_url=UtilConfig.AVATAR_URL,
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
            color=UtilConfig.ERROR_COLOR,
            timestamp=utils.utcnow(),
        )
        self.set_footer(
            text=UtilConfig.FOOTER_TEXT,
            icon_url=UtilConfig.AVATAR_URL,
        )
