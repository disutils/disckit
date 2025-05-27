from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from typing_extensions import override

from disckit.cogs.loader import dis_load_extension

if TYPE_CHECKING:
    from logging import Logger
    from typing import Optional


__all__ = ("dis_load_extension", "BaseCog")


class BaseCog(commands.Cog):
    """The base cog which comes along with basic logging."""

    def __init__(self, logger: Optional[Logger] = None) -> None:
        super().__init__()
        self.logger: Optional[Logger] = logger

    @override
    async def cog_load(self) -> None:
        if self.logger:
            self.logger.info(f"{self.qualified_name} has been loaded.")

    @override
    async def cog_unload(self) -> None:
        if self.logger:
            self.logger.info(f"{self.qualified_name} has been unloaded.")
