from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from discord import ActivityType, Colour

from disckit.utils import default_status_handler

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from types import CoroutineType
    from typing import Any, ClassVar

    from discord.ext.commands import Bot


_BASE_WORKER_COG_PATH: str = "disckit.cogs.worker."


class UtilConfig:
    """The utility class which configures disckit's utilities.

    Attributes
    ----------
    MAIN_COLOR : None | int | Colour
        | The color of the MainEmbed.

    SUCCESS_COLOR : Optional[int, discord.color.Color, tuple[int, int, int]]
        | The color of the SuccessEmbed.

    ERROR_COLOR : Optional[int, discord.color.Color, tuple[int, int, int]]
        | The color of the ErrorEmbed.

    SUCCESS_EMOJI : None | str
        | An emoji used in the title of the SuccessEmbed.

    ERROR_EMOJI : None | str
        | An emoji used in the title of the ErrorEmbed.

    FOOTER_IMAGE : None | str
        | A URL to an image for the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    FOOTER_TEXT : None | str
        | The footer text of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    STATUS_FUNC : tuple[Awaitable[Union[tuple, list, set]], tuple]
        | A tuple having its first element as a coroutine object which will be awaited when-
        | - When the cog first loads.
        | - When the handler is done iterating through all statuses returned from the function.
        | The second element is a tuple containing the extra arguments that can be passed to your
        | custom status handler function. If no arguments have to be passed an empty tuple
        | should suffice.

    STATUS_TYPE : ActivityType
        | The discord acitvity type used by the StatusHandler.

    STATUS_COOLDOWN: None | int
        | A cooldown in seconds for how long a status will play before changing in the `StatusHandler` cog.

    BUG_REPORT_CHANNEL: None | int
        | The channel ID to where the bug reports will be sent to by the `ErrorHandler` cog.

    OWNER_LIST_URL : None | str
        | The URL from which to fetch the list of owner IDs for the bot. If not set, no fetching will occur.
    """

    def __init__(self) -> None:
        raise RuntimeError("Cannot instantiate UtilConfig.")

    MAIN_COLOR: ClassVar[None | int | Colour] = 0x5865F2

    SUCCESS_COLOR: ClassVar[None | int | Colour] = 0x00FF00

    ERROR_COLOR: ClassVar[None | int | Colour] = 0xFF0000

    SUCCESS_EMOJI: ClassVar[str] = "✅"

    ERROR_EMOJI: ClassVar[str] = "❌"

    FOOTER_IMAGE: ClassVar[None | str] = None

    FOOTER_TEXT: ClassVar[None | str] = None

    STATUS_FUNC: ClassVar[
        tuple[
            Callable[
                [Bot, *tuple[Any, ...]], CoroutineType[Any, Any, Sequence[str]]
            ],
            tuple[Any, ...],
        ]
    ] = (
        default_status_handler,
        (),
    )

    STATUS_TYPE: ClassVar[ActivityType] = ActivityType.listening

    STATUS_COOLDOWN: ClassVar[None | float] = None

    BUG_REPORT_CHANNEL: ClassVar[None | int] = None

    OWNER_LIST_URL: ClassVar[None | str] = None

    PAGINATOR_FIRST_PAGE: ClassVar[str] = "⏪"

    PAGINATOR_NEXT_PAGE: ClassVar[str] = "➡️"

    PAGINATOR_PREVIOUS_PAGE: ClassVar[str] = "⬅️"

    PAGINATOR_LAST_PAGE: ClassVar[str] = "⏩"


class CogEnum(StrEnum):
    ERROR_HANDLER = _BASE_WORKER_COG_PATH + "error_handler"
    """An extension for error handling."""

    STATUS_HANDLER = _BASE_WORKER_COG_PATH + "status_handler"
    """An extension for the bot's status handling."""

    OWNER_IDS_HANDLER = _BASE_WORKER_COG_PATH + "owner_ids_handler"
    """An extension for fetching owner IDs in a URL."""
