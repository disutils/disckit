import aiohttp
import logging

from discord.ext import commands, tasks

from disckit.config import UtilConfig

logger = logging.getLogger(__name__)


class OwnerIDsHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.fetch_owner_ids.start()

    async def cog_load(self) -> None:
        print(f"{self.__class__.__name__} has been loaded.")

    async def cog_unload(self) -> None:
        self.fetch_owner_ids.cancel()
        print(f"{self.__class__.__name__} has been unloaded.")

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
                    local_vars = {}
                    exec(data, globals(), local_vars)
                    OWNER_IDS = local_vars.get("OWNER_IDS", set())
                    self.bot.owner_ids = OWNER_IDS
                    logger.info("Owner IDs successfully fetched.")
                else:
                    logger.error(
                        f"Failed to fetch owner IDs. Response Status: {response.status}"
                    )

    @fetch_owner_ids.before_loop
    async def before_fetch_owner_ids(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OwnerIDsHandler(bot))
