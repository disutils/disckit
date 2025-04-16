from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
from discord.ext import commands, tasks

from disckit.config import UtilConfig

if TYPE_CHECKING:
    from discord.ext.commands import Bot


_logger = logging.getLogger(__name__)


class OwnerIDsHandler(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.fetch_owner_ids.start()

    async def cog_load(self) -> None:
        _logger.info(f"{self.qualified_name} has been loaded.")

    async def cog_unload(self) -> None:
        self.fetch_owner_ids.cancel()
        _logger.info(f"{self.qualified_name} has been unloaded.")

    @tasks.loop(hours=12)
    async def fetch_owner_ids(self) -> None:
        url = UtilConfig.OWNER_LIST_URL

        if not url:
            _logger.warning("OWNER_LIST_URL is not set in the configuration.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    local_vars = {}
                    exec(data, globals(), local_vars)
                    OWNER_IDS = local_vars.get("OWNER_IDS", set())
                    self.bot.owner_ids = OWNER_IDS
                    _logger.info("Owner IDs successfully fetched.")
                else:
                    _logger.error(
                        f"Failed to fetch owner IDs. Response Status: {response.status}"
                    )

    @fetch_owner_ids.before_loop
    async def before_fetch_owner_ids(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Bot) -> None:
    await bot.add_cog(OwnerIDsHandler(bot))
