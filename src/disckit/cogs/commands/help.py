import logging
from typing import Any, Optional, Sequence

import discord
from discord import Embed, Interaction, app_commands
from discord.ext.commands import Bot
from discord.ui import Select

from disckit import UtilConfig
from disckit.cogs import BaseCog
from disckit.utils import MainEmbed, MentionTree

logger = logging.getLogger(__name__)


class HelpSelect(Select[Any]):
    def __init__(
        self, valid_cogs: list[str], cog_embed_data: dict[str, Embed]
    ) -> None:
        options: list[discord.SelectOption] = [
            discord.SelectOption(
                label=cog.title(),
                value=cog.lower(),
            )
            for cog in valid_cogs
        ]

        super().__init__(placeholder="Select A Command Menu", options=options)


class HelpCog(BaseCog, name="Help Cog"):
    """The help command based cog."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger)
        self.bot: Bot = bot
        # self.cog_embed_data: dict[str, Embed] = {
        #     "overview": UtilConfig.OVERVIEW_HELP_EMBED
        # }

    async def help_auto_complete(
        self, interaction: Interaction, current: Optional[str]
    ) -> list[app_commands.Choice[str]]:
        cog_copy: list[str] = ["Overview", "All Commands"]
        cog_copy.extend(list(self.bot.cogs.keys()))

        for cog_name in UtilConfig.IGNORE_HELP_COGS:
            cog_copy.remove(cog_name)

        def remove_commands() -> None:
            for cog_name in UtilConfig.OWNER_ONLY_HELP_COGS:
                try:
                    cog_copy.remove(cog_name)
                except ValueError:
                    pass

        if self.bot.owner_id and interaction.user.id != self.bot.owner_id:
            remove_commands()

        elif (
            self.bot.owner_ids
            and interaction.user.id not in self.bot.owner_ids
        ):
            remove_commands()

        commands: list[app_commands.Choice[str]] = [
            app_commands.Choice(name=option.title(), value=option)
            for option in cog_copy
        ]
        return commands

    async def get_all_cog_embeds(self) -> dict[str, list[Embed]]:
        tree: MentionTree = self.bot.tree  # pyright:ignore[reportAssignmentType]
        kwargs: dict[str, discord.Object] = {}
        embed_data: dict[str, list[Embed]] = {}
        cog_command_map: dict[str, str] = {}

        for cog_name, cog_instance in self.bot.cogs.items():
            for command in cog_instance.walk_app_commands():
                if isinstance(command, app_commands.Command):
                    cog_command_map[command.qualified_name] = cog_name

        if UtilConfig.HELP_OWNER_GUILD_ID:
            kwargs["guild"] = discord.Object(UtilConfig.HELP_OWNER_GUILD_ID)

        async for command, mention in tree.walk_mentions(**kwargs):
            command.qualified_name

    @app_commands.command()
    @app_commands.describe(group="The group you want help for.")
    @app_commands.autocomplete(group=help_auto_complete)
    async def help(
        self, interaction: Interaction, group: str = "Overview"
    ) -> None:
        """The bot's help command"""

        await interaction.response.defer()

        group = group.lower()
        valid_cogs = await self.help_auto_complete(
            interaction=interaction, current=None
        )
        valid_cog_names: list[str] = [cog.name.lower() for cog in valid_cogs]

        required_cog = group if group in valid_cog_names else "overview"
        requred_embed = await self.get_cog_embed(required_cog)
