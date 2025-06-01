from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import discord
from discord.app_commands import Choice

from disckit.utils.embeds import ErrorEmbed, MainEmbed, SuccessEmbed

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import (
        Any,
        Optional,
        ParamSpec,
        Tuple,
        TypeGuard,
        TypeVar,
        Union,
    )

    from discord import Client, Guild, Interaction, Thread, User
    from discord.abc import GuildChannel, PrivateChannel
    from discord.ext.commands import Bot

    T_autocomplete = TypeVar("T_autocomplete", str, int, float)

    P = ParamSpec("P")
    T = TypeVar("T")


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


async def default_status_handler(bot: Bot, *args: Any) -> Tuple[str, ...]:
    """The default status handler. The first parameter will always be the
    bot instance which will automatically be passed as argument in the
    status handler.

    This function is called when cog first loads and when the handler is
    done iterating through all the statuses returned from the function.


    Parameters
    ----------
    bot
        | The global bot instance that gets passed to the function automatically.
    *args
        | The extra arguments passed in `UtilUtilConfig.STATUS_FUNC[1]`
        | (The second element is the extra arguments that will be passed on).

    Returns
    --------
    | Heehee hawhaw
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


def type_guarantee(var: Any, *var_types: type[T]) -> TypeGuard[T]:
    """Ensures the type of a variable for type checking purposes only;
    it has no effect at runtime.

    Parameters
    ----------
    var
        The variable to guarentee the type for.
    *var_types
        The types to verify against.
    """

    return True


def make_autocomplete(
    *args: T_autocomplete,
) -> Any:
    """Creates an autocomplete function for the given arguments.

    Parameters
    ----------
    *args
        | Options for the autocomplete

    Returns
    --------
    | A function that can be put in @discord.app_commands.autocomplete

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

    async def autocomplete(_p1: Any, _p2: Any) -> list[Choice[T_autocomplete]]:
        return choices

    return autocomplete


async def sku_check(bot: Client, sku_id: int, user_id: int) -> bool:
    """|coro|

    Checks if a user has purchased a specific SKU package.

    Parameters
    ----------
    bot
        | The bot class.
    sku_id
        | The SKU ID of the package.
    user_id
        | The Discord user ID to check.

    Returns
    -------
    | A bool indicating if the user has subscribed to the package or not.
    """

    sku = discord.Object(id=sku_id)
    user = discord.Object(id=user_id)

    user_entitlements = [
        entitlement
        async for entitlement in bot.entitlements(skus=[sku], user=user)
    ]

    return bool(user_entitlements)


def disallow_bots() -> Callable[..., Any]:
    """A decorator used for not allowing members to pass in a bot user into command params"""

    def decorator(
        func: Callable[P, Awaitable[Optional[T]]],
    ) -> Callable[P, Awaitable[Optional[T]]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            interaction: None | Interaction[Bot] = None
            bot_user: bool = False

            for arg in args + tuple(kwargs.values()):
                if isinstance(arg, discord.Interaction):
                    interaction = arg

                elif isinstance(arg, (discord.Member, discord.User)):
                    bot_user = bot_user or arg.bot

            if bot_user and interaction:
                embed = ErrorEmbed("You cannot interact with bots!")

                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        embed=embed, ephemeral=True
                    )
                return

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def is_owner() -> Callable[..., Any]:
    """A decorator for owner-only slash commands"""

    def decorator(
        func: Callable[P, Awaitable[Optional[T]]],
    ) -> Callable[P, Awaitable[Optional[T]]]:
        """A decorator for owner-only slash commands"""

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
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

    return decorator


async def get_or_fetch_guild(bot: Client, id: int) -> Guild:
    """|coro|

    Tries to fetch the guild object from cache. If it fails, it makes
    an API request to the discord API and return it.

    Parameters
    ----------
    bot
        The bot instance.
    id
        The ID of the guild object you want to obtain.
    """
    return bot.get_guild(id) or await bot.fetch_guild(id)


async def get_or_fetch_user(bot: Client, id: int) -> User:
    """|coro|

    Tries to fetch the user object from cache. If it fails, it makes
    an API request to the discord API and return it.

    Parameters
    ----------
    bot
        The bot instance.
    id
        The ID of the guild object you want to obtain.

    Raises
    ------
    NotFound
        A user with this ID does not exist.
    HTTPException
        Fetching the user failed.
    """

    return bot.get_user(id) or await bot.fetch_user(id)


async def get_or_fetch_channel(
    bot: Client, id: int
) -> Union[PrivateChannel, GuildChannel, Thread]:
    """|coro|

    Tries to fetch the channel object from cache. If it fails, it makes
    an API request to the discord API and return it.

    Parameters
    ----------
    bot
        The bot instance.
    id
        The ID of the channel object you want to obtain.

    Raises
    ------
    InvalidData
        An unknown channel type was received from Discord.
    HTTPException
        Retrieving the channel failed.
    NotFound
        Invalid Channel ID.
    Forbidden
        You do not have permission to fetch this channel.
    """

    return bot.get_channel(id) or await bot.fetch_channel(id)
