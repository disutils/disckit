from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disckit.config import CogEnum, UtilConfig
from disckit.errors import CogLoadError
from disckit.utils import MentionTree

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot, Bot

logger = logging.getLogger(__name__)


async def dis_load_extension(
    bot: AutoShardedBot | Bot,
    *cogs: CogEnum,
    debug_message: bool = True,
) -> None:
    """|coro|
    A custom extension loader specifically for the disckit cogs.

    Parameters
    ----------
    bot
        | The bot instance.

    *cogs
        | The cogs to be loaded from disckit package.

    debug_message
        | The debug message to be printed out when the cog is loaded.
        | Needs to contain one `{}` which is formatted to the cog name
        | being loaded.

    Raises
    ------
    :exc:`CogLoadError`
        | Raised when an error occurrs in loading the cog.
    """

    message = None
    for cog in set(cogs):
        if cog == CogEnum.STATUS_HANDLER:
            if not UtilConfig.STATUS_FUNC:
                message = (
                    "Attribute - `UtilConfig.STATUS_FUNC` needs"
                    " to be set to use StatusHandler cog"
                )

            elif not UtilConfig.STATUS_TYPE:
                message = (
                    "Attribute - `UtilConfig.STATUS_TYPE` needs"
                    "to be set to use StatusHandler cog"
                )

            elif not UtilConfig.STATUS_COOLDOWN:
                message = (
                    "Attribute - `UtilConfig.STATUS_COOLDOWN` needs"
                    " to be set to use StatusHandler cog."
                )

        if cog == CogEnum.ERROR_HANDLER:
            if not UtilConfig.BUG_REPORT_CHANNEL:
                message = (
                    "Attribute - `UtilConfig.BUG_REPORT_CHANNEL` needs"
                    " to be set to use ErrorHandler cog."
                )

        if cog == CogEnum.OWNER_IDS_HANDLER:
            if not UtilConfig.OWNER_LIST_URL:
                message = (
                    "Attribute - `UtilConfig.OWNER_LIST_URL` needs to be"
                    " set to use OwnerIDSHandler cog"
                )

        if cog == CogEnum.HELP_COG:
            if not isinstance(bot.tree, MentionTree):
                message = (
                    "`bot.tree` Needs to be of disckit.utils.MentionTree type. "
                    "Pass in `tree_cls` argument in the initialization as the required type."
                )

        if message:
            raise CogLoadError(message=message, cog=cog)

        if debug_message:
            logger.info(
                f"Loading extension: {cog.name.title().replace(' ', '')}"
            )
        await bot.load_extension(cog.value)
