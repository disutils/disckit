from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle, Embed
from discord.ui import Button, Modal, View

from disckit.config import UtilConfig
from disckit.errors import PaginatorInvalidCurrentPage, PaginatorInvalidPages
from disckit.utils import ErrorEmbed

if TYPE_CHECKING:
    from typing import Any, Sequence

    from discord import Interaction


def create_empty_button() -> Button:
    return Button(label="\u200b", style=ButtonStyle.gray, disabled=True)


class HomeButton(Button):
    def __init__(
        self, home_page: str | Embed, new_view: None | View = None
    ) -> None:
        super().__init__(
            emoji=UtilConfig.PAGINATOR_HOME_PAGE_EMOJI,
            label=UtilConfig.PAGINATOR_HOME_PAGE_LABEL,
            style=UtilConfig.PAGINATOR_HOME_BUTTON_STYLE,
        )
        self.home_page = home_page
        self.new_view = new_view

    async def callback(self, interaction: Interaction) -> None:
        payload = {"view": self.new_view}
        if isinstance(self.home_page, str):
            payload["content"] = self.home_page
        else:
            payload["embed"] = self.home_page

        await interaction.response.edit_message(**payload)


class PageJumpModal(Modal): ...


class Paginator(View):
    def __init__(
        self,
        interaction: Interaction,
        *,
        pages: Sequence[Embed | str],
        current_page: int = 0,
        author: None | int = None,
        timeout: None | float = 180.0,
        home_page: None | Embed | str = None,
        home_view: None | View = None,
        extra_buttons: None | Sequence[Button] = None,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)

        self.total_pages = len(pages)

        if self.total_pages == 0:
            raise PaginatorInvalidPages(
                "Expected a seqence of 1 or more items (Embed | str). Instead got 0 items."
            )

        if current_page > self.total_pages - 1:
            raise PaginatorInvalidCurrentPage(
                f"Expected an integer of range [0, {len(pages) - 1}]. Instead got {current_page}."
            )

        self.interaction = interaction
        self.pages = pages
        self.current_page = current_page
        self.author = author
        self.timeout = timeout
        self.home_page = home_page
        self.home_view = home_view
        self.extra_buttons = list(extra_buttons) if extra_buttons else []
        self.ephemeral = ephemeral

    def send_kwargs(self, page_element: Embed | str) -> dict[str, Any]:
        payload = {"view": self}
        if isinstance(page_element, str):
            payload["content"] = page_element
        else:
            payload["embed"] = page_element
        return payload

    async def start(self) -> None:
        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"

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

        element: Embed | str = self.pages[self.current_page]
        payload_kwargs = self.send_kwargs(element)

        if self.interaction.response.is_done():
            await self.interaction.followup.send(**payload_kwargs)
        else:
            await self.interaction.response.send_message(**payload_kwargs)

    async def update_paginator(self, interaction: Interaction) -> None:
        self.children[
            2
        ].label = f"{self.current_page + 1} / {self.total_pages}"

        if interaction.response.is_done():
            if not interaction.message.id:
                await interaction.followup.send(
                    embed=ErrorEmbed("Message not found to edit.", "Error!")
                )
                return
            await interaction.followup.edit_message(
                interaction.message.id,
                embed=self.pages[self.current_page],
                view=self,
            )

        else:
            await interaction.response.edit_message(
                embed=self.pages[self.current_page], view=self
            )

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_FIRST_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def first_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None:
        await interaction.response.defer()

        self.current_page = 0

        await self.update_paginator(interaction)

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_PREVIOUS_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def previous_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None:
        await interaction.response.defer()

        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = self.total_pages - 1
        await self.update_paginator(interaction)

    @discord.ui.button(label="0/0", disabled=True, style=ButtonStyle.gray)
    async def number_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_NEXT_PAGE_EMOJI,
        style=UtilConfig.PAGINATOR_BUTTON_STYLE,
    )
    async def next_page_callback(
        self, interaction: Interaction, button: Button
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
        self, interaction: Interaction, button: Button
    ) -> None:
        await interaction.response.defer()

        self.current_page = self.total_pages - 1

        await self.update_paginator(interaction)
