import logging
from typing import Any, Optional

import discord
from discord import Embed, Interaction, app_commands
from discord.ext.commands import Bot
from discord.ui import Select, View

from disckit import UtilConfig
from disckit.cogs import BaseCog
from disckit.utils import ErrorEmbed, MainEmbed, MentionTree
from disckit.utils.paginator import Paginator

logger = logging.getLogger(__name__)


class HelpSelect(Select[Any]):
    def __init__(
        self,
        author: int,
        valid_help_options: list[str],
        cog_embed_data: dict[str, list[Embed]],
    ) -> None:
        self.author: int = author
        self.cog_embed_data: dict[str, list[Embed]] = cog_embed_data

        options: list[discord.SelectOption] = [
            discord.SelectOption(
                label=cog.title(),
                value=cog.title(),
            )
            for cog in valid_help_options
        ]

        try:
            del cog_embed_data["Help Cog"]
        except KeyError:
            pass

        super().__init__(
            placeholder="Select A Command Menu",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != self.author:
            await interaction.response.send_message(
                embed=ErrorEmbed("This help command isn't for you!"),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        selected_cog: str = self.values[0]
        if selected_cog == "All Commands":
            all_embeds: list[Any] = []
            owner_cogs: list[str] = [
                name.title() for name in UtilConfig.OWNER_ONLY_HELP_COGS
            ]
            for cog, embeds in self.cog_embed_data.items():
                if cog.title() not in owner_cogs:
                    all_embeds.extend(embeds)

        elif selected_cog == "Overview":
            all_embeds = [UtilConfig.OVERVIEW_HELP_EMBED]

        else:
            all_embeds = self.cog_embed_data[selected_cog]

        view = View()
        view.add_item(self)
        paginator = Paginator(
            interaction,
            author=interaction.user.id,
            pages=all_embeds,
            home_page=UtilConfig.OVERVIEW_HELP_EMBED,
            home_view=view,
        )
        message = await interaction.original_response()
        await paginator.start(message)


class HelpCog(BaseCog, name="Help Cog"):
    """The help command based cog."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger)
        self.bot: Bot = bot

    def partition_split(self, item: list[Any], chunk_size: int) -> list[Any]:
        return [
            item[i : i + chunk_size] for i in range(0, len(item), chunk_size)
        ]

    async def help_auto_complete(
        self, interaction: Interaction, current: Optional[str]
    ) -> list[app_commands.Choice[str]]:
        cog_copy: list[str] = ["Overview", "All Commands"]
        cog_copy.extend(list(self.bot.cogs.keys()))
        cog_copy = [name.title() for name in cog_copy]

        for cog_name in UtilConfig.IGNORE_HELP_COGS:
            try:
                cog_copy.remove(cog_name.title())
            except ValueError:
                logger.warning(
                    "Couldn't find cog: `%s` under `UtilConfig.IGNORE_HELP_COGS`",
                    cog_name.title(),
                )

        def remove_commands() -> None:
            for cog_name in UtilConfig.OWNER_ONLY_HELP_COGS:
                try:
                    cog_copy.remove(cog_name.title())
                except ValueError:
                    logger.warning(
                        "Couldn't find cog: `%s` under `UtilConfig.OWNER_ONLY_HELP_COGS`",
                        cog_name.title(),
                    )

        if self.bot.owner_id and interaction.user.id != self.bot.owner_id:
            remove_commands()

        elif (
            self.bot.owner_ids
            and interaction.user.id not in self.bot.owner_ids
        ):
            remove_commands()

        commands: list[app_commands.Choice[str]] = [
            app_commands.Choice(name=option.title(), value=option.title())
            for option in cog_copy
        ]
        narrowed_commands: list[app_commands.Choice[str]] = []

        if current:
            narrowed_commands = [
                choice
                for choice in commands
                if current.lower() in str(choice.name).lower()
            ][:25]

        return narrowed_commands or commands[:25]

    async def get_all_cog_embeds(self) -> dict[str, list[Embed]]:
        tree: MentionTree = self.bot.tree
        kwargs: dict[str, discord.Object] = {}
        cog_command_description: dict[str, list[str]] = {}
        cog_command_map: dict[str, str] = {}
        cog_command_embed: dict[str, list[Embed]] = {}
        cmd_per_embed: int = 7

        for cog_name, cog_instance in self.bot.cogs.items():
            for command in cog_instance.walk_app_commands():
                if isinstance(command, app_commands.Command):
                    cog_command_map[command.qualified_name] = cog_name

        if UtilConfig.HELP_OWNER_GUILD_ID:
            kwargs["guild"] = discord.Object(UtilConfig.HELP_OWNER_GUILD_ID)

        async for command, mention in tree.walk_mentions(**kwargs):
            cog_command_description.setdefault(
                cog_command_map[command.qualified_name], []
            )
            total_commands = len(
                cog_command_description[
                    cog_command_map[command.qualified_name]
                ]
            )
            cog_command_description[
                cog_command_map[command.qualified_name]
            ].append(
                f"`{total_commands + 1}.` {mention}\n> {command.description}"
            )

        for cog_name, command in cog_command_description.items():
            command_split = self.partition_split(
                cog_command_description[cog_name.title()], cmd_per_embed
            )

            cog_command_embed[cog_name.title()] = []

            for commands in command_split:
                embed = MainEmbed(f"{cog_name.title()}", "\n\n".join(commands))
                cog_command_embed[cog_name.title()].append(embed)

        return cog_command_embed

    @app_commands.command()
    @app_commands.describe(group="The group you want help for.")
    @app_commands.autocomplete(group=help_auto_complete)
    async def help(
        self, interaction: Interaction, group: str = "Overview"
    ) -> None:
        """The bot's help command"""

        await interaction.response.defer()

        group = group.title()
        valid_cogs = await self.help_auto_complete(
            interaction=interaction, current=None
        )
        valid_cog_names: list[str] = [cog.name for cog in valid_cogs]

        required_cog = group if group in valid_cog_names else "Overview"
        requred_embeds = await self.get_all_cog_embeds()

        if required_cog == "All Commands":
            all_embeds: list[Any] = []
            owner_cogs: list[str] = [
                name.title() for name in UtilConfig.OWNER_ONLY_HELP_COGS
            ]
            for cog_name, embeds in requred_embeds.items():
                if cog_name.title() not in owner_cogs:
                    all_embeds.extend(embeds)

        elif required_cog == "Overview":
            all_embeds = [UtilConfig.OVERVIEW_HELP_EMBED]

        else:
            all_embeds = requred_embeds[required_cog]

        valid_cog_names.remove("Overview")
        view = View()
        view.add_item(
            HelpSelect(interaction.user.id, valid_cog_names, requred_embeds)
        )

        if required_cog == "Overview":
            await interaction.followup.send(
                embed=UtilConfig.OVERVIEW_HELP_EMBED, view=view
            )

        else:
            paginator = Paginator(
                interaction,
                author=interaction.user.id,
                pages=all_embeds,
                home_page=UtilConfig.OVERVIEW_HELP_EMBED,
                home_view=view,
            )
            message = await interaction.original_response()
            await paginator.start(message)


async def setup(bot: Bot) -> None:
    await bot.add_cog(HelpCog(bot))
