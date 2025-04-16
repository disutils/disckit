from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from discord import ActivityType, Colour

from disckit.utils import default_status_handler

if TYPE_CHECKING:
    from typing import Awaitable, ClassVar, List, Optional, Set, Tuple, Union

_BASE_WORKER_COG_PATH: str = "disckit.cogs.worker."


class UtilConfig:
    """The utility class which configures disckit's utilities.

    Attributes
    ----------
    MAIN_COLOR : Union[int, Colour, None]
        | The color of the MainEmbed.

    SUCCESS_COLOR : Optional[int, discord.color.Color, Tuple[int, int, int]]
        | The color of the SuccessEmbed.

    ERROR_COLOR : Optional[int, discord.color.Color, Tuple[int, int, int]]
        | The color of the ErrorEmbed.

    SUCCESS_EMOJI : Optional[str]
        | An emoji used in the title of the SuccessEmbed.

    ERROR_EMOJI : Optional[str]
        | An emoji used in the title of the ErrorEmbed.

    FOOTER_IMAGE : Optional[str]
        | A URL to an image for the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    FOOTER_TEXT : Optional[str]
        | The footer text of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    STATUS_FUNC : Tuple[Awaitable[Union[Tuple, List, Set]], Tuple]
        | A tuple having its first element as a coroutine object which will be awaited when-
        | - When the cog first loads.
        | - When the handler is done iterating through all statuses returned from the function.
        | The second element is a tuple containing the extra arguments that can be passed to your
        | custom status handler function. If no arguments have to be passed an empty tuple
        | should suffice.

    STATUS_TYPE : ActivityType
        | The discord acitvity type used by the StatusHandler.

    STATUS_COOLDOWN: Optional[int]
        | A cooldown in seconds for how long a status will play before changing in the `StatusHandler` cog.

    BUG_REPORT_CHANNEL: Optional[int]
        | The channel ID to where the bug reports will be sent to by the `ErrorHandler` cog.

    OWNER_LIST_URL : Optional[str]
        | The URL from which to fetch the list of owner IDs for the bot. If not set, no fetching will occur.
    """

    def __init__(self) -> None:
        raise RuntimeError("Cannot instantiate UtilConfig.")

    MAIN_COLOR: ClassVar[Union[int, Colour, None]] = 0x5865F2

    SUCCESS_COLOR: ClassVar[Union[int, Colour, None]] = 0x00FF00

    ERROR_COLOR: ClassVar[Union[int, Colour, None]] = 0xFF0000

    SUCCESS_EMOJI: ClassVar[str] = "✅"

    ERROR_EMOJI: ClassVar[str] = "❌"

    FOOTER_IMAGE: ClassVar[Optional[str]] = None

    FOOTER_TEXT: ClassVar[Optional[str]] = None

    STATUS_FUNC: ClassVar[
        Tuple[Awaitable[Union[Tuple[str, ...], List[str], Set[str]]], Tuple]
    ] = (
        default_status_handler,
        (),
    )

    STATUS_TYPE: ClassVar[ActivityType] = ActivityType.listening

    STATUS_COOLDOWN: ClassVar[Optional[int]] = None

    BUG_REPORT_CHANNEL: ClassVar[Optional[int]] = None

    OWNER_LIST_URL: ClassVar[Optional[str]] = None


class CogEnum(StrEnum):
    ERROR_HANDLER = _BASE_WORKER_COG_PATH + "error_handler"
    """An extension for error handling."""

    STATUS_HANDLER = _BASE_WORKER_COG_PATH + "status_handler"
    """An extension for the bot's status handling."""

    OWNER_IDS_HANDLER = _BASE_WORKER_COG_PATH + "owner_ids_handler"
    """An extension for fetching owner IDs in a URL."""
