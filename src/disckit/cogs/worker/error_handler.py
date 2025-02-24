import discord
import traceback
import sys

from discord import Interaction, app_commands
from discord.ext import commands
from typing import Optional, List

from disckit.utils import ErrorEmbed
from disckit.config import UtilConfig


class ErrorHandler(commands.Cog, name="Error Handler"):
    """Error handler for global application commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.default_error_handler = app_commands.CommandTree.on_error

    async def cog_load(self) -> None:
        app_commands.CommandTree.on_error = self.on_error
        print(f"{self.__class__.__name__} has been loaded.")

    async def cog_unload(self) -> None:
        app_commands.CommandTree.on_error = self.default_error_handler
        print(f"{self.__class__.__name__} has been unloaded.")

    @staticmethod
    def __get_group_names(
        group: app_commands.Group,
        all_groups: Optional[List[app_commands.Group]] = None,
    ) -> List[str]:
        all_groups = all_groups or []
        all_groups.append(group.name)
        if group.parent is None:
            return all_groups
        ErrorHandler.__get_group_names(group.parent, all_groups)

    @staticmethod
    async def send_response(
        *,
        interaction: Interaction,
        embed: Optional[discord.Embed] = None,
        content: Optional[str] = None,
        ephemeral: bool = False,
    ) -> None:
        """Handles the error response to user."""

        load = {"ephemeral": ephemeral}
        if embed:
            load["embed"] = embed
        if content:
            load["content"] = content

        try:
            await interaction.response.send_message(**load)
        except discord.InteractionResponded:
            await interaction.followup.send(**load)

    @staticmethod
    async def throw_err(
        interaction: Interaction, error: discord.DiscordException
    ) -> None:
        print(
            f"Ignoring exception in command {interaction.command}:",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

        channel = interaction.client.get_channel(
            UtilConfig.BUG_REPORT_CHANNEL
        ) or await interaction.client.fetch_channel(
            UtilConfig.BUG_REPORT_CHANNEL
        )

        if channel is not None:
            if interaction.command:
                final_name = []
                if interaction.command.parent:
                    final_name = ErrorHandler.__get_group_names(
                        interaction.command.parent
                    )
                final_name.append(interaction.command.name)
                name = "/" + (" ".join(final_name))
            else:
                name = "Command not found"

            await channel.send(
                embed=ErrorEmbed(
                    f"```\nError caused by-\nAuthor Name: {interaction.user}"
                    f"\nAuthor ID: {interaction.user.id}\n"
                    f"\nError Type-\n{type(error)}\n"
                    f"\nError Type Description-\n{error.__traceback__.tb_frame}\n"
                    f"\nCause-\n{error.with_traceback(error.__traceback__)}```",
                    title=name,
                )
            )
        embed = ErrorEmbed(
            title="Sorry...",
            description="An unexpected error has occurred.\nThe developers have been notified of it.",
        )
        await ErrorHandler.send_response(interaction=interaction, embed=embed)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        error_embed = ErrorEmbed("Error")

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
                "This command is only available to owners!",
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
                f"you need ``{missing_permissions}`` permission to use this command.",
            )
            error_embed.set_thumbnail(
                url="https://images.disutils.com/bot_assets/assets/access_denied.png"
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed, ephemeral=True
            )

        elif isinstance(error, commands.ChannelNotFound):
            error_embed.description = (
                f"The specified channel {error.argument} was not found."
                "Please pass in a valid channel."
            )
            await ErrorHandler.send_response(
                interaction=interaction, embed=error_embed
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
