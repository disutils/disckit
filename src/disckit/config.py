from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from discord import ActivityType, ButtonStyle, Colour, Embed

from disckit.utils import default_status_handler

if TYPE_CHECKING:
    from typing import (
        Any,
        ClassVar,
        Coroutine,
        List,
        Optional,
        Protocol,
        Sequence,
        Tuple,
        TypeVar,
        Union,
    )

    from discord import Client

    T_contra = TypeVar("T_contra", bound=Client, contravariant=True)

    class StatusHandlerProtocol(Protocol[T_contra]):
        def __call__(
            self, bot: T_contra, *args: Any
        ) -> Coroutine[Any, Any, Union[Tuple[str, ...], List[str]]]: ...


__all__ = ("UtilConfig", "CogEnum")


_BASE_WORKER_COG_PATH: str = "disckit.cogs.worker."
_BASE_COMMAND_COG_PATH: str = "disckit.cogs.commands."


class UtilConfig:
    """The utility class which configures disckit's utilities.

    Attributes
    ----------
    MAIN_COLOR
        | The color of the MainEmbed.

    SUCCESS_COLOR
        | The color of the SuccessEmbed.

    ERROR_COLOR
        | The color of the ErrorEmbed.

    SUCCESS_EMOJI
        | An emoji used in the title of the SuccessEmbed.

    ERROR_EMOJI
        | An emoji used in the title of the ErrorEmbed.

    FOOTER_IMAGE
        | A URL to an image for the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    FOOTER_TEXT
        | The footer text of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    FOOTER_TIMESTAMP
        | Whether to show a timestamp in the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.

    STATUS_FUNC
        | A tuple having its first element as a coroutine object which will be awaited when-
        | - When the cog first loads.
        | - When the handler is done iterating through all statuses returned from the function.
        | The second element is a tuple containing the extra arguments that can be passed to your
        | custom status handler function. If no arguments have to be passed an empty tuple
        | should suffice.

    STATUS_TYPE
        | The discord acitvity type used by the StatusHandler.

    STATUS_COOLDOWN
        | A cooldown in seconds for how long a status will play before changing in the `StatusHandler` cog.

    BUG_REPORT_CHANNEL
        | The channel ID to where the bug reports will be sent to by the `ErrorHandler` cog.

    OWNER_LIST_URL
        | The URL from which to fetch the list of owner IDs for the bot. If not set, no fetching will occur.

    PAGINATOR_BUTTON_STYLE
        | The button style of the paginator buttons.

    PAGINATOR_HOME_BUTTON_STYLE
        | The style for the Home Button in the paginator.

    PAGINATOR_HOME_PAGE_LABEL
        | The label for the home button in the paginator.

    PAGINATOR_HOME_PAGE_EMOJI
        | The emoji for the home button in the paginator.

    PAGINATOR_FIRST_PAGE_EMOJI
        | The emoji for the button controlling the first page in the paginator.

    PAGINATOR_NEXT_PAGE_EMOJI
        | The emoji for the button controlling the next page in the paginator.

    PAGINATOR_PREVIOUS_PAGE_EMOJI
        | The emoji for the button controlling the previous page in the paginator.

    PAGINATOR_LAST_PAGE_EMOJI
        | The emoji for the button controlling the last page in the paginator.

    COOLDOWN_TEXTS
        | The cooldown text used by the cooldown controller.
        | This config needs to have a single placeholder: {}
        | In each of its string elements.

    OWNER_ONLY_HELP_COGS
        | Names of the cogs which are only to be viewed by the owner and
        | not by a regular user in the help command. This only applies to
        | the autocomplete feature while using the command.

    IGNORE_HELP_COGS
        | The names of the cogs to be ignored in the autocomplete feature
        | while running the help command.

    HELP_OWNER_GUILD_ID
        | The guild ID where all commands are synced to for the help command
        | to view them. This includes owner only commands as well.
    """

    def __init__(self) -> None:
        raise RuntimeError("Cannot instantiate UtilConfig.")

    MAIN_COLOR: ClassVar[Optional[Union[int, Colour]]] = 0x5865F2

    SUCCESS_COLOR: ClassVar[Optional[Union[int, Colour]]] = 0x00FF00

    ERROR_COLOR: ClassVar[Optional[Union[int, Colour]]] = 0xFF0000

    SUCCESS_EMOJI: ClassVar[str] = "✅"

    ERROR_EMOJI: ClassVar[str] = "❌"

    FOOTER_IMAGE: ClassVar[Optional[str]] = None

    FOOTER_TEXT: ClassVar[Optional[str]] = None

    FOOTER_TIMESTAMP: ClassVar[bool] = True

    STATUS_FUNC: ClassVar[
        Tuple[StatusHandlerProtocol[Any], Tuple[Any, ...]]
    ] = (
        default_status_handler,
        (),
    )

    STATUS_TYPE: ClassVar[ActivityType] = ActivityType.listening

    STATUS_COOLDOWN: ClassVar[Optional[float]] = None

    BUG_REPORT_CHANNEL: ClassVar[Optional[int]] = None

    OWNER_LIST_URL: ClassVar[Optional[str]] = None

    PAGINATOR_BUTTON_STYLE: ClassVar[ButtonStyle] = ButtonStyle.blurple

    PAGINATOR_HOME_BUTTON_STYLE: ClassVar[ButtonStyle] = ButtonStyle.red

    PAGINATOR_HOME_PAGE_LABEL: ClassVar[Optional[str]] = None

    PAGINATOR_HOME_PAGE_EMOJI: ClassVar[Optional[str]] = "🏠"

    PAGINATOR_FIRST_PAGE_EMOJI: ClassVar[str] = "⏪"

    PAGINATOR_NEXT_PAGE_EMOJI: ClassVar[str] = "➡️"

    PAGINATOR_PREVIOUS_PAGE_EMOJI: ClassVar[str] = "⬅️"

    PAGINATOR_LAST_PAGE_EMOJI: ClassVar[str] = "⏩"

    COOLDOWN_TEXTS: Sequence[str] = (
        "Chill, the command will be available {}",
        "What's the hurry? The command will be available {}.",
        "I appreciate your enthusiasm but the command can be used {}.",
        "Take a deep breath in, a deep breath out. The command will be available {}.",
    )

    OWNER_ONLY_HELP_COGS: Sequence[str] = ()

    IGNORE_HELP_COGS: Sequence[str] = (
        "help cog",
        "status handler",
        "error handler",
        "owner id handler",
    )

    OVERVIEW_HELP_EMBED: Embed = Embed(
        title="Bot's Overview",
        description=(
            "Welcome to the help overview of the bot.\n"
            "Use the select menu from below to see the description of different command groups."
        ),
    )

    HELP_OWNER_GUILD_ID: Optional[int] = None


class CogEnum(StrEnum):
    ERROR_HANDLER = _BASE_WORKER_COG_PATH + "error_handler"
    """An extension for error handling."""

    STATUS_HANDLER = _BASE_WORKER_COG_PATH + "status_handler"
    """An extension for the bot's status handling."""

    OWNER_IDS_HANDLER = _BASE_WORKER_COG_PATH + "owner_id_handler"
    """An extension for fetching owner IDs in a URL."""

    HELP_COG = _BASE_COMMAND_COG_PATH + "help"
    """An extension for the help command."""
