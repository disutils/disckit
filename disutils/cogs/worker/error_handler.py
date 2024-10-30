import discord
import traceback
import sys

from discord import Interaction, app_commands
from discord.ext import commands

from core import Bot
from data.constants.bot_const import BUG_REPORT_CHANNEL
from utils import *


class ErrorHandler(commands.Cog, name="Error Handler"):
    """Error Handling for commands"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.default_error_handler = app_commands.CommandTree.on_error

    async def cog_load(self) -> None:
        app_commands.CommandTree.on_error = self.on_error
        print(f"{self.__class__.__name__} has been loaded.")

    async def cog_unload(self) -> None:
        app_commands.CommandTree.on_error = self.default_error_handler

    async def send_msg(
        self,
        interaction: Interaction,
        embed: None | discord.Embed = None,
        msg: None | str = None,
        ephemeral: bool = False,
    ) -> None:
        """Handles the error response to user."""

        load = {"ephemeral": ephemeral}
        if embed:
            load["embed"] = embed
        if msg:
            load["content"] = msg

        try:
            await interaction.response.send_message(**load)
        except discord.InteractionResponded:
            await interaction.followup.send(**load)

    async def throw_err(
        self, interaction: Interaction, error: discord.DiscordException
    ) -> None:
        print(f"Ignoring exception in command {interaction.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

        channel = self.bot.get_channel(BUG_REPORT_CHANNEL)
        if channel is None:
            channel = await self.bot.fetch_channel(BUG_REPORT_CHANNEL)

        if channel is not None:
            await channel.send(
                embed=ErrorEmbed(
                    f"```\nError caused by-\nAuthor Name: {interaction.user}"
                    f"\nAuthor ID: {interaction.user.id}\n"
                    f"\nError Type-\n{type(error)}\n"
                    f"\nError Type Description-\n{error.__traceback__.tb_frame}\n"
                    f"\nCause-\n{error.with_traceback(error.__traceback__)}```",
                    f"Error in command: {interaction.command.name}",
                )
            )
        embed = ErrorEmbed(
            title="Sorry...",
            description="An unexpected error has occurred. The developers have been notified of it.",
        )
        await self.send_msg(interaction=interaction, embed=embed)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:

        if isinstance(interaction.channel, discord.DMChannel):
            return

        elif (
            isinstance(error, commands.CommandError)
            and str(error) == "User is blacklisted."
        ):
            return

        elif isinstance(error, discord.NotFound):
            if error.code == 10008:
                return

        elif isinstance(error, commands.errors.NotOwner):
            error_embed = ErrorEmbed(
                title="Error",
                description="You do not have the required permissions to use this command.\n"
                "This command is only available to owners!",
            )
            await self.send_msg(interaction=interaction, embed=error_embed)

        # elif isinstance(error, commands.MissingRequiredArgument):
        #    param = error.param.name
        #    command = interaction.command.qualified_name if interaction.command else None
        #    description = command.help or "No description available."
        #
        #    embed = MainEmbed(
        #        title="Information", description=f"Missing Argument: `{param}`"
        #    )
        #    embed.set_thumbnail(
        #        url="https://images.disutils.com/bot_assets/assets/missing_arg.png"
        #    )
        #    embed.add_field(name="Description", value=description, inline=False)
        #    await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, commands.BotMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            error_embed = ErrorEmbed(
                title="Error",
                description=f"I don't have the required permissions for this command, "
                f"I need ``{missing_permissions}`` permission to proceed with this command.",
            )
            error_embed.set_thumbnail(
                url="https://images.disutils.com/bot_assets/assets/missing_perms.png"
            )
            await self.send_msg(
                interaction=interaction, embed=error_embed, ephemeral=True
            )

        elif isinstance(error, commands.errors.MissingPermissions):

            missing_permissions = ", ".join(error.missing_permissions)
            error_embed = ErrorEmbed(
                title="Error",
                description=f"You don't have the required permissions for this command, "
                f"you need ``{missing_permissions}`` permission to use this command.",
            )
            error_embed.set_thumbnail(
                url="https://images.disutils.com/bot_assets/assets/access_denied.png"
            )
            await self.send_msg(
                interaction=interaction, embed=error_embed, ephemeral=True
            )

        # elif isinstance(
        #    error, (commands.CommandInvokeError, commands.errors.HybridCommandError)
        # ):
        #    original = getattr(error, "original", error)
        #    if isinstance(original, discord.Forbidden):
        #        member = ctx.message.mentions[0] if ctx.message.mentions else None
        #
        #        if member:
        #            if ctx.author.top_role < member.top_role:
        #                error_embed = ErrorEmbed(
        #                    title="Error",
        #                    description="You cannot perform this action due to role hierarchy.",
        #                )
        #                await ctx.send(embed=error_embed, ephemeral=True)
        #            elif ctx.guild.me.top_role <= member.top_role:
        #                error_embed = ErrorEmbed(
        #                    title="Error",
        #                    description="I cannot perform this action due to role hierarchy.",
        #                )
        #                await ctx.send(embed=error_embed, ephemeral=True)

        elif isinstance(
            error, (commands.ChannelNotFound, commands.errors.ChannelNotFound)
        ):
            error_embed = ErrorEmbed(
                title="Error",
                description=f"The specified channel {error.argument} was not found."
                "Please pass in a valid channel.",
            )
            await self.send_msg(interaction=interaction, embed=error_embed)

        else:
            await self.throw_err(interaction=interaction, error=error)


async def setup(bot: Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))