from __future__ import annotations

from discord import Colour, ActivityType, Locale
from typing import (
    Optional,
    TypeAlias,
    Union,
    ClassVar,
    Awaitable,
    Tuple,
    Dict,
    List,
    Set,
)
from enum import StrEnum
from disckit.utils import default_status_handler

TypeColor: TypeAlias = Union[int, Colour, Tuple[int, int, int]]
_BASE_WORKER_COG_PATH: str = "disckit.cogs.worker."


class UtilConfig:
    """The utility class which configures disckit's utilities."""

    MAIN_COLOR: ClassVar[TypeColor] = 0x5865F2
    """Class Attribute
    ---
    MAIN_COLOR: :class:`Optional[int, discord.color.Color, Tuple[int, int, int]]`

        The color of the MainEmbed.
    """

    SUCCESS_COLOR: ClassVar[TypeColor] = 0x00FF00
    """Class Attribute
    ---
    SUCCESS_COLOR: :class:`Optional[int, discord.color.Color, Tuple[int, int, int]]`

        The color of the SuccessEmbed.
    """

    ERROR_COLOR: ClassVar[TypeColor] = 0xFF0000
    """Class Attribute
    ---
    ERROR_COLOR: :class:`Optional[int, discord.color.Color, Tuple[int, int, int]]`

        The color of the ErrorEmbed.
    """

    SUCCESS_EMOJI: ClassVar[str] = "✅"
    """Class Attribute
    ---
    SUCCESS_EMOJI: :class:`Optional[str]`

        An emoji used in the title of the SuccessEmbed.
    """

    ERROR_EMOJI: ClassVar[str] = "❌"
    """Class Attribute
    ---
    ERROR_EMOJI: :class:`Optional[str]`

        An emoji used in the title of the ErrorEmbed.
    """

    FOOTER_IMAGE: ClassVar[Optional[str]] = None
    """Class Attribute
    ---
    FOOTER_IMAGE: :class:`Optional[str]`

        A URL to an image for the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.
    """

    FOOTER_TEXT: ClassVar[Optional[str]] = None
    """Class Attribute
    ---
    FOOTER_TEXT: :class:`Optional[str]`

        The footer text of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.
    """

    STATUS_FUNC: ClassVar[
        Tuple[Awaitable[Union[Tuple[str, ...], List[str], Set[str]]], Tuple]
    ] = (
        default_status_handler,
        (),
    )
    """Class Attribute
    ---
    STATUS_FUNC: :class:`Tuple[Awaitable[Union[Tuple, List, Set]], Tuple]`

        A tuple having its first element as a coroutine object which will be awaited when-<br>
        - When the cog first loads.<br>
        - When the handler is done iterating through all statuses returned from the function.<br>
        The second element is a tuple containing the extra arguments that can be passed to your
        custom status handler function. If no arguments have to be passed an empty tuple
        should suffice.
    """

    STATUS_TYPE: ClassVar[ActivityType] = ActivityType.listening
    """Class Attribute
    ---
    STATUS_TYPE: :class:`ActivityType`

        The discord acitvity type used by the StatusHandler.
    """

    STATUS_COOLDOWN: ClassVar[Optional[int]] = None
    """Class Attribute
    ---
    STATUS_COOLDOWN: :class:`Optional[int]`

        A cooldown in seconds for how long a status will play before changing in the `StatusHandler` cog.
    """

    BUG_REPORT_CHANNEL: ClassVar[Optional[int]] = None
    """Class Attribute
    ---
    BUG_REPORT_CHANNEL: :class:`Optional[int]`

        The channel ID to where the bug reports will be sent to by the `ErrorHandler` cog.
    """

    LEMMA_TRANS_GROUPS: ClassVar[Optional[Dict[Locale, str]]] = None
    """Class Attribute
    ---

    LEMMA_TRANS_PATHS: :class:`Optional[Dict[Locale, str]]`

        A :class:`discord.Locale` object mapping to the folder / file containing it's respective group
        translation files only. The LemmaTranslator only works for translating command paramters and
        description only.
    """

    LEMMA_TRANS_COMMANDS: ClassVar[Optional[Dict[Locale, str]]] = None
    """Class Attribute
    ---

    LEMMA_TRANS_PATHS: :class:`Optional[Dict[Locale, str]]`

        A :class:`discord.Locale` object mapping to the folder / file containing it's respective command
        translation files. The LemmaTranslator only works for translating command paramters and description
        only.
    """


class CogEnum(StrEnum):
    ERROR_HANDLER: str = _BASE_WORKER_COG_PATH + "error_handler"
    """An extension for error handling."""

    STATUS_HANDLER: str = _BASE_WORKER_COG_PATH + "status_handler"
    """An extension for the bot's status handling."""
