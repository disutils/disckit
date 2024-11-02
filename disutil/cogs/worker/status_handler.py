import discord
from discord.ext import commands, tasks

from disutil.config import UtilConfig


class StatusHandler(commands.Cog):
    """Cog for handling bot's dynamic status."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.status = None

    async def cog_load(self) -> None:
        self.status_task.start()
        print(f"{self.__class__.__name__} has been loaded.")

    async def cog_unload(self) -> None:
        self.status_task.cancel()
        print(f"{self.__class__.__name__} has been unloaded.")

    @tasks.loop(seconds=UtilConfig.STATUS_COOLDOWN)
    async def status_task(self) -> None:
        await self.bot.wait_until_ready()

        if self.status is None:
            self.status = iter(
                await UtilConfig.STATUS_FUNC[0](
                    self.bot, *await UtilConfig.STATUS_FUNC[1]
                )
            )

        try:
            current_status = next(self.status)
        except StopIteration:
            self.status = iter(
                await UtilConfig.STATUS_FUNC[0](
                    self.bot, *await UtilConfig.STATUS_FUNC[1]
                )
            )
            current_status = next(self.status)

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=current_status
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatusHandler(bot))
