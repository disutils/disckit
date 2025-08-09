from __future__ import annotations

import logging
import traceback
from typing import TYPE_CHECKING, Any

import discord
from discord import ButtonStyle, Embed
from discord.ui import Button

from disckit.config import UtilConfig
from disckit.errors import PaginatorInvalidCurrentPage, PaginatorInvalidPages
from disckit.utils import ErrorEmbed
from disckit.utils.ui import BaseModal, BaseView

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Union

    from discord import Emoji, Interaction, Message, PartialEmoji
    from discord.ui import TextInput, View


__all__ = ("create_empty_button", "HomeButton", "PageJumpModal", "Paginator")


logger = logging.getLogger(__name__)


def create_empty_button(
    label: str = "\u200b",
    style: ButtonStyle = ButtonStyle.gray,
    disabled: bool = True,
    custom_id: Optional[str] = None,
    emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
    row: int | None = None,
) -> Button[Any]:
    """Creates a placeholder button with no callback."""

    return Button(
        label=label,
        style=style,
        disabled=disabled,
        custom_id=custom_id,
        emoji=emoji,
        row=row,
    )


class HomeButton(Button["Any"]):
    def __init__(
        self,
        home_page: Union[str, Embed],
        author: Optional[int],
        new_view: Optional[View] = None,
    ) -> None:
        super().__init__(
            emoji=UtilConfig.PAGINATOR_HOME_PAGE_EMOJI,
            label=UtilConfig.PAGINATOR_HOME_PAGE_LABEL,
            style=UtilConfig.PAGINATOR_HOME_BUTTON_STYLE,
        )
        self.author: Optional[int] = author
        self.home_page: Union[str, Embed] = home_page
        self.new_view: Optional[View] = new_view

    async def callback(self, interaction: Interaction) -> None:
        if self.author and interaction.user.id != self.author:
            await interaction.response.send_message(
                embed=ErrorEmbed("This interaction is not for you!")
            )
            return

        payload: dict[str, Any] = {"view": self.new_view}
        if isinstance(self.home_page, str):
            payload["content"] = self.home_page
            payload["embed"] = None
        else:
            payload["embed"] = self.home_page
            payload["content"] = None

        await interaction.response.edit_message(**payload)


class PageJumpModal(BaseModal, title="Jump to Page"):
    page_number: TextInput[PageJumpModal] = discord.ui.TextInput(
        label="Enter the page number you want to jump to",
        placeholder="...",
        min_length=1,
        max_length=100,
        style=discord.TextStyle.short,
    )

    def __init__(
        self,
        paginator_view: Paginator,
        author: Optional[int] = None,
    ) -> None:
        super().__init__(author=author)

        self.paginator_view: Paginator = paginator_view
        self.author: Optional[int] = author

        self.page_number.placeholder = f"1 - {self.paginator_view.total_pages}"

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        if self.author and interaction.user.id != self.author:
            await interaction.followup.send(
                embed=ErrorEmbed("This interaction is not for you!"),
                ephemeral=True,
            )
            return

        if not self.page_number.value.isdigit():
            await interaction.followup.send(
                embed=ErrorEmbed("Please enter an integer."), ephemeral=True
            )
            return

        page_num = int(self.page_number.value)

        if page_num < 1 or page_num > self.paginator_view.total_pages:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    f"Invalid page number! Please enter a number from 1 - {self.paginator_view.total_pages}"
                ),
                ephemeral=True,
            )
            return

        self.paginator_view.current_page = page_num - 1
        await self.paginator_view.update_paginator(interaction=interaction)


class Paginator(BaseView):
    """A custom, easy-to-use paginator for your bot.
    It can paginate through a list / tuple of strings or embeds.

    Attributes
    ----------
    interaction
        The interaction for the paginator to respond to.
    pages
        The pages to paginate over.
    total_pages
        The total number of pages.
    current_page
        The current page it is on.
    timeout
        The amount of seconds in which the paginator view will time out in.
    author
        The author of the paginator, disallowing anyone else to use it.
    home_page
        Adds a home button if this is supplied
    home_view
        An optional home view which is activated when the home button is used.
    extra_buttons
        Extra buttons to be added to the paginator.
    ephemeral
        A bool for if the paginator needs to be ephemeral or not.
    """

    def __init__(
        self,
        interaction: Interaction,
        *,
        pages: Sequence[Union[str, Embed]],
        start_page: int = 0,
        author: Optional[int] = None,
        home_page: Optional[Union[Embed, str]] = None,
        home_view: Optional[View] = None,
        extra_buttons: Optional[Sequence[Button[Any]]] = None,
        extra_buttons_format: bool = True,
        ephemeral: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        interaction
            | The interaction for the paginator to respond to.
        pages
            | The pages to paginate over.
        start_page
            | The starting page for the paginator to begin.
        author
            | The author of the paginator, disallowing anyone else to use it.
        home_page
            | Adds a home button if this is supplied
        home_view
            | An optional home view which is activated when the home button is used.
        extra_buttons
            | Extra buttons to be added to the paginator.
        extra_buttons_format
            | If `True` is passed, it formats the buttons in a symmetrical format.
        ephemeral
            | A bool for if the paginator needs to be ephemeral or not.
        """

        super().__init__(author=author, **kwargs)

        self.total_pages: int = len(pages)

        if self.total_pages == 0:
            raise PaginatorInvalidPages(
                "Expected a seqence of 1 or more items (Embed | str). Instead got 0 items."
            )

        if start_page > self.total_pages - 1:
            raise PaginatorInvalidCurrentPage(
                f"Expected an integer of range [0, {len(pages) - 1}]. Instead got {start_page}."
            )

        self.interaction: Interaction = interaction
        self.pages: Sequence[Union[str, Embed]] = pages
        self.current_page: int = start_page
        self.author: Optional[int] = author
        self.home_page: Optional[Union[Embed, str]] = home_page
        self.home_view: Optional[View] = home_view
        self.extra_buttons: list[Button[Any]] = (
            list(extra_buttons) if extra_buttons else []
        )
        self.extra_buttons_format: bool = extra_buttons_format
        self.ephemeral: bool = ephemeral

    def _send_kwargs(
        self, page_element: Union[Embed, str], send_ephemeral: bool = False
    ) -> dict[str, Any]:
        if send_ephemeral is True:
            payload: dict[str, Any] = {
                "view": self,
                "ephemeral": self.ephemeral,
            }
        else:
            payload: dict[str, Any] = {"view": self}

        if isinstance(page_element, str):
            payload["content"] = page_element
            payload["embed"] = None
        else:
            payload["embed"] = page_element
            payload["content"] = None
        return payload

    def _add_all_items(self) -> None:
        for button in self.extra_buttons:
            self.add_item(button)

    async def start(
        self,
        message: Optional[Message] = None,
        edit_original_resp: bool = False,
    ) -> None:
        """Starts the entire paginator.

        Parameters
        ----------
        message : Optional[Message]
            If it is not None, the paginator starts by editing this
            message instead of sending a new one

        edit_original_resp: bool
            If it's set to true it will edit the original response in case it was an ephemeral, otherwise defaults to
            false. Note: Only use this if the original response of your interaction was ephemeral.
        """

        self.message: Optional[Message] = message

        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"  # pyright:ignore[reportAttributeAccessIssue]

        if self.total_pages == 1:
            for button_index in range(5):
                self.children[button_index].disabled = True  # pyright:ignore[reportAttributeAccessIssue]

        if self.home_page:
            self.add_item(create_empty_button())
            self.add_item(create_empty_button())
            self.add_item(
                HomeButton(self.home_page, self.author, self.home_view)
            )
            self.add_item(create_empty_button())
            self.add_item(create_empty_button())

        total_extra_buttons = len(self.extra_buttons)
        full_rows = 0

        if total_extra_buttons > 0 and self.extra_buttons_format:
            if total_extra_buttons > 5:
                full_rows = total_extra_buttons // 5
                buttons_slice = self.extra_buttons[: full_rows * 5]
                self.extra_buttons = self.extra_buttons[full_rows * 5 :]

                for button in buttons_slice:
                    self.add_item(button)

                total_extra_buttons = len(self.extra_buttons)

            if total_extra_buttons == 1:
                self.add_item(create_empty_button())
                self.add_item(create_empty_button())
                self.add_item(self.extra_buttons[0])
                self.add_item(create_empty_button())
                self.add_item(create_empty_button())

            elif total_extra_buttons % 4 == 0 and total_extra_buttons // 4 < (
                4 - full_rows
            ):
                for button_index in range(0, len(self.extra_buttons) - 1, 4):
                    self.add_item(self.extra_buttons[button_index])
                    self.add_item(self.extra_buttons[button_index + 1])
                    self.add_item(create_empty_button())
                    self.add_item(self.extra_buttons[button_index + 2])
                    self.add_item(self.extra_buttons[button_index + 3])

            elif total_extra_buttons % 3 == 0 and total_extra_buttons // 3 < (
                4 - full_rows
            ):
                for button_index in range(0, len(self.extra_buttons) - 1, 3):
                    self.add_item(create_empty_button())
                    self.add_item(self.extra_buttons[button_index])
                    self.add_item(self.extra_buttons[button_index + 1])
                    self.add_item(self.extra_buttons[button_index + 2])
                    self.add_item(create_empty_button())

            elif total_extra_buttons % 2 == 0 and total_extra_buttons // 2 < (
                4 - full_rows
            ):
                for button_index in range(0, len(self.extra_buttons) - 1, 2):
                    self.add_item(create_empty_button())
                    self.add_item(self.extra_buttons[button_index])
                    self.add_item(create_empty_button())
                    self.add_item(self.extra_buttons[button_index + 1])
                    self.add_item(create_empty_button())

            else:
                self._add_all_items()

        else:
            self._add_all_items()

        element: Union[Embed, str] = self.pages[self.current_page]

        if edit_original_resp is True:
            payload_kwargs = self._send_kwargs(element)
            await self.interaction.edit_original_response(**payload_kwargs)

        else:
            if self.interaction.response.is_done():
                if self.message:
                    payload_kwargs = self._send_kwargs(element)
                    await self.interaction.followup.edit_message(
                        self.message.id, **payload_kwargs
                    )

                else:
                    payload_kwargs = self._send_kwargs(element, True)
                    await self.interaction.followup.send(**payload_kwargs)
            else:
                if self.message:
                    payload_kwargs = self._send_kwargs(element)
                    await self.interaction.response.defer()
                    await self.interaction.followup.edit_message(
                        self.message.id, **payload_kwargs
                    )

                else:
                    payload_kwargs = self._send_kwargs(element, True)
                    await self.interaction.response.send_message(
                        **payload_kwargs
                    )

        if self._disable_on_timeout and not self.message:
            self.message = await self.interaction.original_response()

    async def update_paginator(self, interaction: Interaction) -> None:
        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"  # pyright:ignore[reportAttributeAccessIssue]
        kwargs: dict[str, Any] = self._send_kwargs(
            self.pages[self.current_page]
        )

        if interaction.response.is_done():
            if not interaction.message:
                await interaction.followup.send(
                    embed=ErrorEmbed("Error!", "Message not found to edit.")
                )
                logger.error("Could not find interaction message to edit.")
                traceback.print_stack()
                return

            await interaction.followup.edit_message(
                interaction.message.id, **kwargs
            )

        else:
            await interaction.response.edit_message(**kwargs)

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_FIRST_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def first_page_callback(
        self, interaction: Interaction, button: Button[Any]
    ) -> None:
        await interaction.response.defer()

        self.current_page = 0

        await self.update_paginator(interaction)

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_PREVIOUS_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def previous_page_callback(
        self, interaction: Interaction, button: Button[Any]
    ) -> None:
        await interaction.response.defer()

        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = self.total_pages - 1
        await self.update_paginator(interaction)

    @discord.ui.button(label="0/0", style=ButtonStyle.gray)
    async def number_page_callback(
        self, interaction: Interaction, button: Button[Any]
    ) -> None:
        await interaction.response.send_modal(PageJumpModal(self, self.author))

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_NEXT_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def next_page_callback(
        self, interaction: Interaction, button: Button[Any]
    ) -> None:
        await interaction.response.defer()

        self.current_page += 1
        if self.current_page > self.total_pages - 1:
            self.current_page = 0
        await self.update_paginator(interaction)

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_LAST_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def last_page_callback(
        self, interaction: Interaction, button: Button[Any]
    ) -> None:
        await interaction.response.defer()

        self.current_page = self.total_pages - 1

        await self.update_paginator(interaction)
