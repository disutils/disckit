import datetime
import functools
import random
from typing import TYPE_CHECKING

import discord
from discord import Interaction

from disckit.utils import ErrorEmbed, sku_check

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, TypeAlias

OptionalUser: TypeAlias = None | discord.Member | discord.User | int
OptionalCommand: TypeAlias = None | str

cooldown_data = {"users": {}}


class CoolDown:
    @staticmethod
    def cool_down(
        time: int, owner_bypass: bool = False, sku_id: int = None
    ) -> Callable:
        """A command decorator to handle cool downs and cool down replies automatically.

        Parameters
        ----------
        time: :class:`int`
            How long for the cool down to last in seconds.
        owner_bypass: :class:`bool`, default `False`
            Whether to allow bypassing the cooldown for owners. Optional and defaults to False.
        sku_id: :class:`int`, default `None`
            The SKU ID to check for bypassing the cooldown. Optional and defaults to None.

        Returns
        --------
        Optional[:class:`DatabaseClass`]
            A :class:`DatabaseClass` of containing the required attributes.
            Returns `None` when the record doesn't exist and `auto_create` is set to `False`.
        """

        def decorator(func: Callable) -> Coroutine:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Callable:
                nonlocal time

                interaction: Interaction = locals()["args"][1]
                cooldown_check = CoolDown.check(interaction)

                sku = await sku_check(
                    bot=interaction.client,
                    sku_id=sku_id,
                    user_id=interaction.user.id,
                )

                if (
                    cooldown_check[0]
                    or (owner_bypass and interaction.user.id in OWNER_IDS)
                    or sku
                ):
                    CoolDown.add(time, interaction)
                    await func(*args, **kwargs)
                else:
                    cooldown_text = random.choice(COOLDOWN_TEXTS).format(
                        cooldown_check[1]
                    )
                    await interaction.response.send_message(
                        embed=ErrorEmbed(cooldown_text), ephemeral=True
                    )

            return wrapper

        return decorator

    @staticmethod
    def add(
        time_: int,
        interaction: Interaction,
        user: OptionalUser = None,
        command: OptionalCommand = None,
    ) -> None:
        """
        Adds the cool down to the user
        @command_: The command's name
        @interaction : The Interaction of the user
        """

        if user is not None:
            assert isinstance(user, (discord.Member, discord.User, int)), (
                f"Expected [discord.Member, discord.User, int] instead got {type(user)}"
            )

            if isinstance(user, (discord.Member, discord.User)):
                user = user.id
        else:
            user = interaction.user.id
        command = interaction.command.name if command is None else command
        current = datetime.datetime.now()

        cooldown_data["users"].setdefault(command, {})
        cooldown_data["users"][command][user] = current + datetime.timedelta(
            seconds=time_
        )

    @staticmethod
    def check(
        interaction: Interaction,
        user: OptionalUser = None,
        command: OptionalCommand = None,
    ) -> tuple[bool, None | str]:
        """
        Checks whether the user is under a cool down or not
        @command_: The command's name
        @interaction : The Interaction of the user
        """

        if user is not None:
            assert isinstance(user, (discord.Member, discord.User, int)), (
                f"Expected [discord.Member, discord.User, int] instead got {type(user)}"
            )

            if isinstance(user, (discord.Member, discord.User)):
                user = user.id
        else:
            user = interaction.user.id
        command = interaction.command.name if command is None else command
        current = datetime.datetime.now()

        try:
            cooldown = cooldown_data["users"][command][user]
        except KeyError:
            return (True, None)

        if current > cooldown:
            try:
                del cooldown_data["users"][command][user]
            except KeyError:
                pass
            finally:
                return (True, None)

        else:
            cooldown = f"<t:{round(cooldown_data['users'][command][user].timestamp())}:R>"
            return (False, cooldown)

    @staticmethod
    def reset(
        interaction: Interaction,
        user: OptionalUser = None,
        command: OptionalCommand = None,
    ) -> None:
        """
        Removes the cool down from the user
        @command_: The command's name
        @interaction : The Interaction of the user
        """

        if user is not None:
            assert isinstance(user, (discord.Member, discord.User, int)), (
                f"Expected [discord.Member, discord.User, int] instead got {type(user)}"
            )

            if isinstance(user, (discord.Member, discord.User)):
                user = user.id
        else:
            user = interaction.user.id
        command = interaction.command.name if command is None else command

        try:
            del cooldown_data["users"][command][user]
        except KeyError:
            pass
