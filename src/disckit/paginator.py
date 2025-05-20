from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle
from discord.ui.view import View

from disckit.config import UtilConfig

if TYPE_CHECKING:
    from typing import Any, Sequence

    from discord import Button, Embed, Interaction


class Paginator(View):
    def __init__(
        self,
        interaction: Interaction,
        pages: Sequence[Embed | str],
        current_page: int = 0,
        new_view: None | View = None,
        timeout: None | float = 180.0,
        home_button: bool = True,
        home_embed: None | Embed = None,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)

        if current_page > len(pages) - 1:
            raise ValueError(
                f"Expected an integer of range [0, {len(pages - 1)}]. Instead got {current_page}."
            )

        self.interaction = interaction
        self.pages = pages
        self.current_page = current_page
        self.new_view = new_view
        self.timeout = timeout
        self.home_button = home_button
        self.home_embed = home_embed
        self.ephemeral = ephemeral

    def send_kwargs(self, page_element: Embed | str) -> dict[str, Any]:
        payload = {"view": self}
        if isinstance(page_element, str):
            payload["content"] = page_element
        else:
            payload["embed"] = page_element
        return payload

    async def start(self) -> None:
        element: Embed | str = self.pages[self.current_page]
        kwargs = self.send_kwargs(element)

        self.children[2].label = f"{self.current_page + 1} / {len(self.pages)}"

        if self.interaction.response.is_done():
            await self.interaction.followup.send(**kwargs)
        else:
            await self.interaction.response.send_message(**kwargs)

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_FIRST_PAGE, style=ButtonStyle.gray
    )
    async def first_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_PREVIOUS_PAGE, style=ButtonStyle.gray
    )
    async def previous_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(label="0/5", disabled=True, style=ButtonStyle.gray)
    async def number_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_NEXT_PAGE, style=ButtonStyle.gray
    )
    async def next_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(
        emoji=UtilConfig.PAGINATOR_LAST_PAGE, style=ButtonStyle.gray
    )
    async def last_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...
