from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING

import discord
from discord.ui import Modal, View
from discord.utils import MISSING

from disckit import UtilConfig
from disckit.utils import ErrorEmbed

if TYPE_CHECKING:
    from typing import Any, Optional, Union

    from discord import Interaction, InteractionMessage, Member, Message, User
    from discord.ui import Item


__all__ = ("BaseView", "BaseModal")


logger = logging.getLogger(__name__)


class BaseView(View):
    """A custom base view which extends `discord.ui.View`
    to provide more inbuilt features.

    Parameters
    ----------
    author
        | The author of the `View`. If set to `None` anyone can interact with the `View`.
    timeout
        | In how many seconds the view will timeout.
    disable_on_timeout
        | If set to `True` it will disable all items in the view when it times out.
    stop_on_timeout
        | Stops the view from listening to any further events on timeout.
    """

    def __init__(
        self,
        author: Optional[Union[int, User, Member]] = None,
        timeout: Optional[float] = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
    ) -> None:
        super().__init__(timeout=timeout)

        self.message: Optional[Union[Message, InteractionMessage]] = None

        self._author: Optional[Union[int, User, Member]] = author
        if isinstance(self._author, (discord.User, discord.Member)):
            self._author = self._author.id
        self._disable_on_timeout: bool = disable_on_timeout
        self._stop_on_timeout: bool = stop_on_timeout

    def disable_all_items(self) -> None:
        """Disables all items in the View when called."""

        for item in self.children:
            item.disabled = True  # pyright:ignore[reportAttributeAccessIssue]

    async def on_timeout(self) -> None:
        if self._disable_on_timeout:
            self.disable_all_items()
            if self.message:
                try:
                    await self.message.edit(view=self)
                except discord.errors.NotFound:
                    pass
                except discord.errors.HTTPException as e:
                    if e.code == 50027:
                        logger.error(
                            "Invalid Webhook Token: Unable to edit the message."
                        )
                    elif e.code == 10008:
                        logger.error(
                            "Unknown Message: The message was deleted."
                        )
                    else:
                        raise e
            else:
                raise Warning(
                    f"{traceback.format_exc()}\n\n"
                    f"BaseView.message was not defined in view: {self} to disable the items.",
                )

        if self._stop_on_timeout:
            self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self._author is None or interaction.user.id == self._author:
            return True

        await interaction.response.send_message(
            embed=ErrorEmbed("This interaction is not for you!"),
            ephemeral=True,
        )
        return False

    async def on_error(
        self, interaction: Interaction, error: Exception, item: Item[Any]
    ) -> None:
        if not UtilConfig.BUG_REPORT_CHANNEL:
            return await super().on_error(interaction, error, item)

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=ErrorEmbed(
                    "Sorry :(",
                    "An unexpected error has occurred. The developers have been notified of this.",
                )
            )
        await interaction.response.send_message(
            embed=ErrorEmbed(
                "Sorry :(",
                "An unexpected error has occurred. The developers have been notified of this.",
            )
        )

        print(
            f"Ignoring exception in view {item.view or self} for item {item}:",
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

        frame = (
            error.__traceback__.tb_frame if error.__traceback__ else "Unkown"
        )

        description = (
            "```"
            f"\nError in view-\n{item.view or self}\n"
            f"\nError in item-\n{item}\n"
            f"\nError caused by-\nAuthor Name: {interaction.user}"
            f"\nAuthor ID: {interaction.user.id}\n"
            f"\nError Type-\n{type(error)}\n"
            f"\nError Type Description-\n{frame}\n"
            f"\nCause-\n{error.with_traceback(error.__traceback__)}"
            "```"
        )

        await channel.send(  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            embed=ErrorEmbed(
                "Error caused in a view",
                description,
            )
        )


class BaseModal(Modal):
    """A custom base modal which extends `discord.ui.Modal`
    to provide more inbuilt features.

    Parameters
    -----------
    title
        | The title of the modal.
        | Can only be up to 45 characters.
    timeout
        | Timeout in seconds from last interaction with the UI before no longer accepting input.
        | If ``None`` then there is no timeout.
    custom_id
        | The ID of the modal that gets received during an interaction.
        | If not given then one is generated for you.
        | Can only be up to 100 characters.
    author
        | The author of the modal. Disallows anyone else to use the modal.
    """

    def __init__(
        self,
        *,
        title: str = MISSING,
        timeout: Optional[float] = None,
        custom_id: str = MISSING,
        author: Optional[Union[int, User, Member]] = None,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

        self._author: Optional[Union[int, User, Member]] = author
        if isinstance(self._author, (discord.User, discord.Member)):
            self._author = self._author.id

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self._author is None or interaction.user.id == self._author:
            return True

        await interaction.response.send_message(
            embed=ErrorEmbed("This interaction is not for you!"),
            ephemeral=True,
        )
        return False

    async def on_error(
        self, interaction: Interaction, error: Exception
    ) -> None:
        if not UtilConfig.BUG_REPORT_CHANNEL:
            await super().on_error(interaction, error)
            return

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=ErrorEmbed(
                    "Sorry :(",
                    "An unexpected error has occurred. The developers have been notified of this.",
                )
            )
        await interaction.response.send_message(
            embed=ErrorEmbed(
                "Sorry :(",
                "An unexpected error has occurred. The developers have been notified of this.",
            )
        )

        print(
            f"Ignoring exception in modal {self}:",
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

        frame = (
            error.__traceback__.tb_frame if error.__traceback__ else "Unkown"
        )

        description = (
            "```"
            f"\nError in modal-\n{self}\n"
            f"\nError caused by-\nAuthor Name: {interaction.user}"
            f"\nAuthor ID: {interaction.user.id}\n"
            f"\nError Type-\n{type(error)}\n"
            f"\nError Type Description-\n{frame}\n"
            f"\nCause-\n{error.with_traceback(error.__traceback__)}"
            "```"
        )

        await channel.send(  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            embed=ErrorEmbed(
                "Error caused in a modal",
                description,
            )
        )
