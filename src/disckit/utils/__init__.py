from typing import Tuple, Any
from discord.ext import commands
from src.disckit.utils.embeds import *


async def default_status_handler(bot: commands.Bot, *args: Any) -> Tuple[str, ...]:
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
        f"Slash commands!",
    )

    return status
