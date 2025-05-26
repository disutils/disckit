from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle, Embed
from discord.ui import Button

from disckit.config import UtilConfig
from disckit.errors import PaginatorInvalidCurrentPage, PaginatorInvalidPages
from disckit.utils import ErrorEmbed
from disckit.utils.ui import BaseModal, BaseView

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Union

    from discord import Interaction, Message
    from discord.ui import TextInput, View


def create_empty_button() -> Button[Any]:
    return Button(label="\u200b", style=ButtonStyle.gray, disabled=True)


class HomeButton(Button[Any | "Paginator"]):
    def __init__(
        self, home_page: Union[str, Embed], new_view: Optional[View] = None
    ) -> None:
        super().__init__(
            emoji=UtilConfig.PAGINATOR_HOME_PAGE_EMOJI,
            label=UtilConfig.PAGINATOR_HOME_PAGE_LABEL,
            style=UtilConfig.PAGINATOR_HOME_BUTTON_STYLE,
        )
        self.home_page: Union[str, Embed] = home_page
        self.new_view: Optional[View] = new_view

    async def callback(self, interaction: Interaction) -> None:
        payload: dict[str, Any] = {"view": self.new_view}
        if isinstance(self.home_page, str):
            payload["content"] = self.home_page
        else:
            payload["embed"] = self.home_page

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
    def __init__(
        self,
        interaction: Interaction,
        *,
        pages: Sequence[Union[Embed, str]],
        current_page: int = 0,
        author: Optional[int] = None,
        timeout: Optional[float] = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
        home_page: Optional[Union[Embed, str]] = None,
        home_view: Optional[View] = None,
        extra_buttons: Optional[Sequence[Button[Any]]] = None,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(
            author=author,
            timeout=timeout,
            disable_on_timeout=disable_on_timeout,
            stop_on_timeout=stop_on_timeout,
        )

        self.total_pages: int = len(pages)

        if self.total_pages == 0:
            raise PaginatorInvalidPages(
                "Expected a seqence of 1 or more items (Embed | str). Instead got 0 items."
            )

        if current_page > self.total_pages - 1:
            raise PaginatorInvalidCurrentPage(
                f"Expected an integer of range [0, {len(pages) - 1}]. Instead got {current_page}."
            )

        self.interaction: Interaction = interaction
        self.pages: Sequence[Union[Embed, str]] = pages
        self.current_page: int = current_page
        self.author: Optional[int] = author
        self.home_page: Optional[Union[Embed, str]] = home_page
        self.home_view: Optional[View] = home_view
        self.extra_buttons: list[Button[Any]] = (
            list(extra_buttons) if extra_buttons else []
        )
        self.ephemeral: bool = ephemeral

    def send_kwargs(self, page_element: Union[Embed, str]) -> dict[str, Any]:
        payload: dict[str, Any] = {"view": self}
        if isinstance(page_element, str):
            payload["content"] = page_element
        else:
            payload["embed"] = page_element
        return payload

    async def start(self, message: Optional[Message] = None) -> None:
        self.message: Optional[Message] = message

        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"  # pyright:ignore[reportAttributeAccessIssue]

        if self.home_page:
            self.extra_buttons.append(
                HomeButton(self.home_page, self.home_view)
            )

        total_extra_buttons = len(self.extra_buttons)

        if total_extra_buttons == 1:
            self.add_item(create_empty_button())
            self.add_item(create_empty_button())
            self.add_item(self.extra_buttons[0])
            self.add_item(create_empty_button())
            self.add_item(create_empty_button())

        elif total_extra_buttons == 2:
            self.add_item(create_empty_button())
            self.add_item(self.extra_buttons[0])
            self.add_item(create_empty_button())
            self.add_item(self.extra_buttons[1])
            self.add_item(create_empty_button())

        elif total_extra_buttons == 3:
            self.add_item(create_empty_button())
            self.add_item(self.extra_buttons[0])
            self.add_item(self.extra_buttons[1])
            self.add_item(self.extra_buttons[2])
            self.add_item(create_empty_button())

        elif total_extra_buttons > 3:
            for button in self.extra_buttons:
                self.add_item(button)

        element: Union[Embed, str] = self.pages[self.current_page]
        payload_kwargs = self.send_kwargs(element)

        if self.interaction.response.is_done():
            await self.interaction.followup.send(**payload_kwargs)
        else:
            await self.interaction.response.send_message(**payload_kwargs)

        if self._disable_on_timeout and not self.message:
            self.message = await self.interaction.original_response()

    async def update_paginator(self, interaction: Interaction) -> None:
        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"  # pyright:ignore[reportAttributeAccessIssue]
        kwargs = self.send_kwargs(self.pages[self.current_page])

        if interaction.response.is_done():
            if not interaction.message:
                await interaction.followup.send(
                    embed=ErrorEmbed("Message not found to edit.", "Error!")
                )
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
