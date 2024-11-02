from discord.ext import commands
from typing import Optional

from disutil.config import CogEnum, UtilConfig
from disutil.errors import CogLoadError


async def dis_load_extension(
    bot: commands.Bot,
    *cogs: CogEnum,
    debug_message: Optional[str] = "Loading extension: {}",
) -> None:
    """|coro|
    A custom extension loader specifically for the disutil-dpy cogs.

    Parameters
    ----------
    bot: :class:`commands.Bot`
        The bot instance.

    *cogs: :class:`CogEnum`
        The cogs to be loaded from disutil-dpy package.

    debug_message: :class:`Optional[str]`
        The debug message to be printed out when the cog is loaded.

    Raises
    ------
    :class:`CogLoadError`
        Raised when an error occurrs in loading the cog.
    """

    message = None
    for cog in cogs:
        if cog == CogEnum.STATUS_HANDLER:
            if UtilConfig.STATUS_COOLDOWN is None:
                message = f"Attribute: `UtilConfig.STATUS_COOLDOWN` needs"
                " to be set before runtime to use StatusHandler cog."

        if cog == CogEnum.ERROR_HANDLER:
            if UtilConfig.BUG_REPORT_CHANNEL is None:
                message = f"Attribute: `UtilConfig.BUG_REPORT_CHANNEL` needs"
                " to be set before runtime to use ErrorHandler cog."

        if message:
            raise CogLoadError(message=message, cog=cog)

        await bot.load_extension(cog.value)
        if debug_message:
            print(debug_message.format(cog.name.title().replace(" ", "")))
