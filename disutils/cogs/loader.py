from discord.ext import commands
from typing import Optional

from disutils import CogEnum


async def dis_load_extension(
    bot: commands.Bot,
    *cogs: CogEnum,
    debug_message: Optional[str] = "Loading extension: {}",
) -> None:
    for cog in cogs:
        await bot.load_extension(cog.value)
        if debug_message:
            print(debug_message.format(cog.name.title().replace(" ", "")))
