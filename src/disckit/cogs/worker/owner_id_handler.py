from __future__ import annotations

import ast
import logging
from typing import TYPE_CHECKING

import aiohttp
from discord.ext import tasks
from typing_extensions import override

from disckit.cogs import BaseCog
from disckit.config import UtilConfig

if TYPE_CHECKING:
    from discord.ext.commands import Bot


logger = logging.getLogger(__name__)


class OwnerIDHandler(BaseCog, name="Owner ID Handler"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger)
        self.bot: Bot = bot
        self.fetch_owner_ids.start()

    @override
    async def cog_load(self) -> None:
        await super().cog_load()

    @override
    async def cog_unload(self) -> None:
        self.fetch_owner_ids.cancel()
        await super().cog_unload()

    @tasks.loop(hours=12)
    async def fetch_owner_ids(self) -> None:
        url = UtilConfig.OWNER_LIST_URL

        if not url:
            logger.warning("OWNER_LIST_URL is not set in the configuration.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    OWNER_IDS = ast.literal_eval(data)
                    self.bot.owner_ids = set(OWNER_IDS)
                    logger.info("Owner IDs successfully fetched.")
                else:
                    logger.error(
                        f"Failed to fetch owner IDs. Response Status: {response.status}"
                    )

    @fetch_owner_ids.before_loop
    async def before_fetch_owner_ids(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Bot) -> None:
    await bot.add_cog(OwnerIDHandler(bot))
