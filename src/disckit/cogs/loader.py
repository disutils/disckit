from discord.ext import commands
from typing import Optional

from disckit.config import CogEnum, UtilConfig
from disckit.errors import CogLoadError


async def dis_load_extension(
    bot: commands.Bot,
    *cogs: CogEnum,
    debug_message: Optional[str] = "Loading extension: {}",
) -> None:
    """|coro|
    A custom extension loader specifically for the disckit cogs.

    Parameters
    ----------
    bot: :class:`commands.Bot`
        The bot instance.

    *cogs: :class:`CogEnum`
        The cogs to be loaded from disckit package.

    debug_message: :class:`Optional[str]`
        The debug message to be printed out when the cog is loaded.
        Needs to contain one `{}` which is formatted to the cog name
        being loaded.

    Raises
    ------
    :class:`CogLoadError`
        Raised when an error occurrs in loading the cog.
    """

    message = None
    for cog in set(cogs):
        if cog == CogEnum.STATUS_HANDLER:
            if not UtilConfig.STATUS_FUNC:
                message = (
                    f"Attribute - `UtilConfig.STATUS_FUNC` needs"
                    " to be set to use StatusHandler cog"
                )

            elif not UtilConfig.STATUS_TYPE:
                message = (
                    f"Attribute - `UtilConfig.STATUS_TYPE` needs"
                    "to be set to use StatusHandler cog"
                )

            elif not UtilConfig.STATUS_COOLDOWN:
                message = (
                    f"Attribute - `UtilConfig.STATUS_COOLDOWN` needs"
                    " to be set to use StatusHandler cog."
                )

        if cog == CogEnum.ERROR_HANDLER:
            if not UtilConfig.BUG_REPORT_CHANNEL:
                message = (
                    f"Attribute - `UtilConfig.BUG_REPORT_CHANNEL` needs"
                    " to be set to use ErrorHandler cog."
                )

        if message:
            raise CogLoadError(message=message, cog=cog)

        await bot.load_extension(cog.value)
        if debug_message:
            print(debug_message.format(cog.name.title().replace(" ", "")))
