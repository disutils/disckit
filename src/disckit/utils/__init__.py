from __future__ import annotations

from typing import TYPE_CHECKING
from discord.app_commands import Choice
from disckit.utils.embeds import SuccessEmbed, MainEmbed, ErrorEmbed

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ext.commands import Bot
    from typing import Any, Awaitable, Callable, List, Tuple, TypeVar

    _T = TypeVar("T", str, int, float)


__all__ = (
    "MainEmbed",
    "SuccessEmbed",
    "ErrorEmbed",
    "default_status_handler",
    "make_autocomplete",
)


async def default_status_handler(bot: Bot, *args: Any) -> Tuple[str, ...]:
    """The default status handler. The first parameter will always be the
    bot instance which will automatically be passed as argument in the
    status handler.

    This function is called when cog first loads and when the handler is
    done iterating through all the statuses returned from the function.


    Parameters
    ----------
    bot: :class:`commands.Bot`
        The global bot instance that gets passed to the function automatically.

    *args: :class:`Any`
        The extra arguments passed in `UtilUtilConfig.STATUS_FUNC[1]`
        (The second element is the extra arguments that will be passed on).

    Returns
    --------
    :class:`Tuple` [:class:`str`, ...]
        Heehee hawhaw
    """

    users = len(bot.users)
    guilds = len(bot.guilds)
    status = (
        # Prefixed by "Listening to" as the default ActivityType
        # (UtilConfig.STATUS_TYPE = ActivityType.listening).
        f"{users:,} users",
        f"humans from {guilds:,} servers",
        "Slash commands!",
    )

    return status


def make_autocomplete(
    *args: _T,
) -> Callable[[Interaction, str], Awaitable[list[Choice[_T]]]]:
    """
    Creates an autocomplete function for the given arguments.

    Parameters
    ----------
        *args: :class:`str`: Options for the autocomplete

    Returns
    --------
        A function that can be put in @discord.app_commands.autocomplete

    Usage
    ------
        ```
        @app_commands.autocomplete(choice=make_autocomplete("Heads", "Tails"))
        @app_commands.command(name="coin-flip")
        async def coin_flip(
            self, interaction: discord.Interaction, choice: str
        ): ...
        ```
    """
    choices = [Choice(name=str(arg), value=arg) for arg in args]

    async def autocomplete(_, __) -> List[Choice[_T]]:  # noqa ANN001
        return choices

    return autocomplete
