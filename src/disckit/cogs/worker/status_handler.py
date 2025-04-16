from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

from disckit.config import UtilConfig

if TYPE_CHECKING:
    from typing import Iterator, Optional

    from discord.ext.commands import Bot

_logger = logging.getLogger(__name__)


class StatusHandler(commands.Cog, name="Status Handler"):
    """Cog for handling bot's dynamic status."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.status: Optional[Iterator[str]] = None

    async def cog_load(self) -> None:
        self.status_task.start()
        _logger.info(f"{self.qualified_name} has been loaded.")

    async def cog_unload(self) -> None:
        self.status_task.cancel()
        _logger.info(f"{self.qualified_name} has been unloaded.")

    @tasks.loop(seconds=UtilConfig.STATUS_COOLDOWN)
    async def status_task(self) -> None:
        await self.bot.wait_until_ready()

        if self.status is None:
            self.status = await self._get_iter()

        try:
            current_status = next(self.status)
        except StopIteration:
            self.status = await self._get_iter()
            current_status = next(self.status)

        await self.bot.change_presence(
            activity=discord.Activity(
                type=UtilConfig.STATUS_TYPE, name=current_status
            )
        )

    async def _get_iter(self) -> Iterator[str]:
        return iter(
            await UtilConfig.STATUS_FUNC[0](
                self.bot, *UtilConfig.STATUS_FUNC[1]
            )
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(StatusHandler(bot))
