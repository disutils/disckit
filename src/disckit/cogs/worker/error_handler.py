from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from typing_extensions import override

from disckit.cogs import BaseCog
from disckit.config import UtilConfig
from disckit.utils import ErrorEmbed

if TYPE_CHECKING:
    from typing import Any, Optional

    from discord import DiscordException, Embed
    from discord.app_commands import AppCommandError, Group
    from discord.ext.commands import Bot

logger = logging.getLogger(__name__)


class ErrorHandler(BaseCog, name="Error Handler"):
    """Error handler for global application commands."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger)
        self.bot: Bot = bot
        self.default_error_handler = app_commands.CommandTree.on_error  # pyright:ignore[reportUnannotatedClassAttribute]

    @override
    async def cog_load(self) -> None:
        app_commands.CommandTree.on_error = self.on_error  # pyright:ignore[reportAttributeAccessIssue]
        await super().cog_load()

    @override
    async def cog_unload(self) -> None:
        app_commands.CommandTree.on_error = self.default_error_handler
        await super().cog_unload()

    @staticmethod
    def _get_group_names(
        group: Group,
        all_groups: None | list[str] = None,
    ) -> list[str]:
        all_groups = all_groups or []
        all_groups.append(group.name)
        if group.parent is None:
            return all_groups
        return ErrorHandler._get_group_names(group.parent, all_groups)

    @staticmethod
    async def send_response(
        *,
        interaction: Interaction,
        embed: Optional[Embed] = None,
        content: Optional[str] = None,
        ephemeral: bool = False,
    ) -> None:
        """Handles the error response to user."""

        load: dict[str, Any] = {"ephemeral": ephemeral}
        if embed:
            load["embed"] = embed
        if content:
            load["content"] = content

        try:
            if interaction.response.is_done():
                await interaction.followup.send(**load)
            else:
                await interaction.response.send_message(**load)
        except discord.InteractionResponded:
            await interaction.followup.send(**load)

    @staticmethod
    async def throw_err(
        interaction: Interaction, error: DiscordException
    ) -> None:
        print(
            f"Ignoring exception in command {interaction.command}:",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

        channel = interaction.client.get_channel(
            UtilConfig.BUG_REPORT_CHANNEL  # pyright:ignore[reportArgumentType]
        ) or await interaction.client.fetch_channel(
            UtilConfig.BUG_REPORT_CHANNEL  # pyright:ignore[reportArgumentType]
        )

        name: str = "Command not found"
        if interaction.command:
            final_name = []
            if (
                not isinstance(interaction.command, app_commands.ContextMenu)
                and interaction.command.parent
            ):
                final_name = ErrorHandler._get_group_names(
                    interaction.command.parent
                )
            final_name.append(interaction.command.name)
            name: str = "/" + (" ".join(final_name))

        await channel.send(  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            embed=ErrorEmbed(
                name,
                f"```\nError caused by-\nAuthor Name: {interaction.user}"
                f"\nAuthor ID: {interaction.user.id}\n"
                f"\nError Type-\n{type(error)}\n"
                f"\nError Type Description-\n{error.__traceback__.tb_frame if error.__traceback__ else None}\n"
                f"\nCause-\n{error.with_traceback(error.__traceback__)}```",
            )
        )
        embed = ErrorEmbed(
            "Sorry...",
            "An unexpected error has occurred.\nThe developers have been notified of it.",
        )
        await ErrorHandler.send_response(interaction=interaction, embed=embed)

    async def on_error(
        self,
        interaction: Interaction,
        error: AppCommandError,
    ) -> None:
        error_embed = ErrorEmbed(title="Error")

        if isinstance(interaction.channel, discord.DMChannel):
            return

        elif (
            isinstance(error, commands.CommandError)
            and str(error) == "User is blacklisted."
        ):  # Custom error that is raised by disutils bots for blacklisting users.
            return

        elif isinstance(error, discord.NotFound):
            if error.code == 10008:
                return

        elif isinstance(error, commands.errors.NotOwner):
            error_embed.description = (
                "You do not have the required permissions to use this command.\n"
                "This command is only available to owners!"
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed
            )

        elif isinstance(error, app_commands.BotMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            error_embed.description = (
                f"I don't have the required permissions for this command, "
                f"I need ``{missing_permissions}`` permission to proceed with this command."
            )
            error_embed.set_thumbnail(
                url="https://images.disutils.com/bot_assets/assets/missing_perms.png"
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed, ephemeral=True
            )

        elif isinstance(error, app_commands.MissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            error_embed.description = (
                f"You don't have the required permissions for this command, "
                f"you need ``{missing_permissions}`` permission to use this command."
            )
            error_embed.set_thumbnail(
                url="https://images.disutils.com/bot_assets/assets/access_denied.png"
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed, ephemeral=True
            )

        elif isinstance(error, app_commands.CommandSignatureMismatch):
            error_embed.description = (
                f"The signature of the command {error.command.name} seems to be different"
                " by the one provided by discord. To fix this issue please request the developers"
                " to sync the commands. If the issue still persists please contact the devs."
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed
            )

        else:
            await self.throw_err(interaction=interaction, error=error)


async def setup(bot: Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
