from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import discord
from discord.app_commands import Choice

from disckit.utils.embeds import ErrorEmbed, MainEmbed, SuccessEmbed

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine
    from functools import _Wrapped  # pyright:ignore[reportPrivateUsage]
    from types import CoroutineType
    from typing import Any, TypeVar

    from discord import Interaction
    from discord.ext.commands import Bot

    _T = TypeVar("_T", str, int, float)


__all__ = (
    "MainEmbed",
    "SuccessEmbed",
    "ErrorEmbed",
    "default_status_handler",
    "make_autocomplete",
    "sku_check",
    "disallow_bots",
    "is_owner",
)


async def default_status_handler(bot: Bot, *args: Any) -> tuple[str, ...]:  # pyright:ignore[reportUnusedParameter]
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

    async def autocomplete(_p1: Any, _p2: Any) -> list[Choice[_T]]:  # pyright:ignore[reportUnusedParameter]
        return choices

    return autocomplete


async def sku_check(bot: Bot, sku_id: int, user_id: int) -> bool:
    """|coro|

    Checks if a user has purchased a specific SKU package.

    Parameters
    ----------
    bot: :class:`int`
        The bot class.
    sku_id: :class:`int`
        The SKU ID of the package.
    user_id: :class:`int`
        The Discord user ID to check.
    """

    sku = discord.Object(id=sku_id)
    user = discord.Object(id=user_id)

    user_entitlements = [
        entitlement
        async for entitlement in bot.entitlements(skus=[sku], user=user)
    ]

    return bool(user_entitlements)


def disallow_bots(
    func: Callable[..., Coroutine[Any, Any, None]],
) -> None | _Wrapped[..., Any, ..., CoroutineType[Any, Any, None]]:
    """A decorator used for not allowing members to pass in a bot user into command params"""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> None:
        interaction: None | Interaction[Bot] = None
        bot_user: bool = False

        for arg in args + tuple(kwargs.values()):
            if isinstance(arg, discord.Interaction):
                interaction = arg

            elif isinstance(arg, (discord.Member, discord.User)):
                bot_user = bot_user or arg.bot

        if bot_user and interaction:
            embed = ErrorEmbed("You cannot interact with bots!")
            try:
                await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            except discord.InteractionResponded:
                await interaction.followup.send(embed=embed, ephemeral=True)
            return
        await func(*args, **kwargs)

    return wrapper


def is_owner(
    func: Callable[..., Coroutine[Any, Any, None]],
) -> None | _Wrapped[..., Any, ..., CoroutineType[Any, Any, None]]:
    """A decorator for owner-only slash commands"""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> None:
        interaction: None | Interaction[Bot] = None

        for arg in args + tuple(kwargs.values()):
            if isinstance(arg, discord.Interaction):
                interaction = arg
                break

        if interaction and interaction.client.owner_ids:
            if interaction.user.id in interaction.client.owner_ids:
                await func(*args, **kwargs)

            else:
                embed = ErrorEmbed("This command is owner only!")
                try:
                    await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                except discord.InteractionResponded:
                    await interaction.followup.send(
                        embed=embed, ephemeral=True
                    )
        else:
            await func(*args, **kwargs)

    return wrapper
