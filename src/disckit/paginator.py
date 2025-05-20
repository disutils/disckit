from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle
from discord.ui.view import View

from disckit.config import UtilConfig

if TYPE_CHECKING:
    from typing import Sequence

    from discord import Embed, Interaction
    from discord import Button 


class Paginator(View):
    def __init__(
        self,
        interaction: Interaction,
        pages: Sequence[Embed | str],
        current_page: int = 0,
        per_page: int = 1,
        new_view: None | View = None,
        timeout: None | float = 180.0,
        home_button: bool = True,
        home_embed: None | Embed = None,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.pages = pages
        self.current_page = current_page
        self.per_page = per_page
        self.new_view = new_view
        self.timeout = timeout
        self.home_button = home_button
        self.home_embed = home_embed
        self.ephemeral = ephemeral

    async def start(self) -> None:
        self.interaction.message

    @discord.ui.button(emoji=UtilConfig.PAGINATOR_FIRST_PAGE, style=ButtonStyle.gray)
    async def first_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(emoji=UtilConfig.PAGINATOR_PREVIOUS_PAGE, style=ButtonStyle.gray)
    async def previous_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(disabled=True, style=ButtonStyle.gray)
    async def number_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(emoji=UtilConfig.PAGINATOR_NEXT_PAGE, style=ButtonStyle.gray)
    async def next_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...

    @discord.ui.button(emoji=UtilConfig.PAGINATOR_LAST_PAGE, style=ButtonStyle.gray)
    async def last_page_callback(
        self, interaction: Interaction, button: Button
    ) -> None: ...


