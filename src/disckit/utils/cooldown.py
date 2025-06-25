from __future__ import annotations

import datetime
import functools
import logging
import random
from enum import Enum, auto
from typing import TYPE_CHECKING, overload

import discord
from discord import Interaction

from disckit import UtilConfig
from disckit.errors import (
    UnkownCooldownCommand,
    UnkownCooldownContext,
    UnkownCooldownInteraction,
)
from disckit.utils import ErrorEmbed, sku_check_guild, sku_check_user

if TYPE_CHECKING:
    from typing import (
        Any,
        Awaitable,
        Callable,
        Literal,
        Optional,
        ParamSpec,
        Sequence,
        Tuple,
        TypeVar,
        Union,
    )

    P = ParamSpec("P")
    T = TypeVar("T")


__all__ = ("CoolDownBucket", "CoolDown")


logger = logging.getLogger(__name__)


class CoolDownBucket(Enum):
    USER = auto()
    GUILD = auto()
    CHANNEL = auto()


class CoolDown:
    owner_ids: Optional[Sequence[int]] = None
    owner_bypass: bool = False

    cooldown_data: dict[
        CoolDownBucket, dict[str, dict[int, datetime.datetime]]
    ] = {
        CoolDownBucket.USER: {},
        CoolDownBucket.GUILD: {},
        CoolDownBucket.CHANNEL: {},
    }

    @overload
    @staticmethod
    def cooldown(
        time: Union[float, int],
        bucket_type: Literal[CoolDownBucket.USER, CoolDownBucket.GUILD] = ...,
        sku_id: int = ...,
    ) -> Callable[..., Any]: ...

    @overload
    @staticmethod
    def cooldown(
        time: Union[float, int],
        bucket_type: CoolDownBucket = ...,
        sku_id: None = ...,
    ) -> Callable[..., Any]: ...

    @staticmethod
    def cooldown(
        time: Union[float, int],
        bucket_type: CoolDownBucket = CoolDownBucket.USER,
        sku_id: Optional[int] = None,
    ) -> Callable[..., Any]:
        """A command decorator to handle cool downs and cool down replies automatically.

        Parameters
        ----------
        time
            | How long for the cool down to last in seconds.
        bucket_type
            | The bucket type for which the cooldown needs to be in.
        sku_id
            | The SKU ID to check for bypassing the cooldown. Optional and defaults to None.
            | The bucket type needs to be of `CoolDownBucket.USER` if sku_id is supplied.
        """

        def decorator(
            func: Callable[P, Awaitable[Optional[T]]],
        ) -> Callable[P, Awaitable[Optional[T]]]:
            @functools.wraps(func)
            async def wrapper(
                *args: P.args, **kwargs: P.kwargs
            ) -> Optional[T]:
                nonlocal time

                interaction: Optional[Interaction] = None
                cooldown_check: Tuple[bool, Optional[str]] = (True, None)
                sku: bool = False

                for arg in args + tuple(kwargs.values()):
                    if isinstance(arg, discord.Interaction):
                        interaction = arg

                if not isinstance(interaction, discord.Interaction):
                    raise UnkownCooldownInteraction(
                        f"Cannot find the interaction object of the command: {func.__name__}"
                    )

                if CoolDown.owner_bypass:
                    if not CoolDown.owner_ids:
                        logger.error(
                            "`CoolDown.owner_ids` contains falsey data while `CoolDown.owner_bypass` is enabled."
                            "\nHence couldn't determine owner ids to bypass."
                        )
                else:
                    cooldown_check = CoolDown.check(
                        interaction=interaction, bucket_type=bucket_type
                    )

                if sku_id:
                    if bucket_type == CoolDownBucket.USER:
                        sku = await sku_check_user(
                            bot=interaction.client,
                            sku_id=sku_id,
                            user_id=interaction.user.id,
                        )

                    elif bucket_type == CoolDownBucket.GUILD:
                        sku = await sku_check_guild(
                            bot=interaction.client,
                            sku_id=sku_id,
                            guild_id=interaction.user.id,
                        )

                if cooldown_check[0] or sku:
                    CoolDown.add(
                        time=time,
                        interaction=interaction,
                        bucket_type=bucket_type,
                    )
                    return await func(*args, **kwargs)

                cooldown_text = random.choice(
                    UtilConfig.COOLDOWN_TEXTS
                ).format(cooldown_check[1])

                await interaction.response.send_message(
                    embed=ErrorEmbed(cooldown_text), ephemeral=True
                )

            return wrapper

        return decorator

    @staticmethod
    def _get_context(
        bucket_type: CoolDownBucket, interaction: Interaction
    ) -> int:
        primary_context: int

        if bucket_type == CoolDownBucket.USER:
            primary_context = interaction.user.id

        elif bucket_type == CoolDownBucket.GUILD:
            if interaction.guild is None:
                raise UnkownCooldownContext(
                    "Couldn't obtain guild object for bucket type `CoolDownBucket.GUILD`"
                    "\nMake sure the command is being ran in a server."
                )
            primary_context = interaction.guild.id

        elif bucket_type == CoolDownBucket.CHANNEL:
            if interaction.channel is None:
                raise UnkownCooldownContext(
                    "Couldn't obtain channel object for bucket type `CoolDownBucket.CHANNEL`"
                    "\nMake sure the command is being ran in a server."
                )
            primary_context = interaction.channel.id

        return primary_context

    @staticmethod
    def add(
        time: Union[float, int],
        interaction: Interaction,
        bucket_type: CoolDownBucket,
        command_name: Optional[str] = None,
    ) -> None:
        """Adds the cool down to the respective bucket type.

        Parameters
        ----------
        time
            | How long for the cool down to last in seconds.
        interaction
            | The interaction object associated with the command.
        bucket_type
            | The bucket type on which the cooldown should act upon.
        command_name
            | An optional command name to give. This will be choosen over `interaction.command.name` if given.
        """

        if interaction.command is None and command_name is None:
            raise UnkownCooldownCommand("Couldn't determine command name.")

        command = command_name or interaction.command.name  # pyright:ignore[reportOptionalMemberAccess]
        primary_context = CoolDown._get_context(
            bucket_type=bucket_type, interaction=interaction
        )
        current = datetime.datetime.now()

        CoolDown.cooldown_data[bucket_type].setdefault(command, {})
        CoolDown.cooldown_data[bucket_type][command][primary_context] = (
            current + datetime.timedelta(seconds=time)
        )

    @overload
    @staticmethod
    def check(  # pyright:ignore[reportOverlappingOverload]
        interaction: Interaction,
        bucket_type: CoolDownBucket,
        command_name: Optional[str] = None,
        cooldown_return: Literal["string"] = ...,
    ) -> Tuple[bool, Optional[str]]: ...

    @overload
    @staticmethod
    def check(
        interaction: Interaction,
        bucket_type: CoolDownBucket,
        command_name: Optional[str] = None,
        cooldown_return: Literal["datetime"] = ...,
    ) -> Tuple[bool, Optional[datetime.datetime]]: ...

    @staticmethod
    def check(
        interaction: Interaction,
        bucket_type: CoolDownBucket,
        command_name: Optional[str] = None,
        cooldown_return: Literal["datetime", "string"] = "string",
    ) -> Tuple[bool, Optional[Union[str, datetime.datetime]]]:
        """Checks the cooldown for the respective bucket type.

        Parameters
        ----------
        interaction
            | The interaction object associated with the command.
        bucket_type
            | The bucket type on which the cooldown should act upon.
        command_name
            | An optional command name to give. This will be choosen over `interaction.command.name` if given.

        Returns
        -------
        | Returns a tuple where the first element is a bool. If the bool is `False` the user is under cooldown.
        | The second element is either a relative timestamp string or a datetime object of when the cooldown gets
        | over. If the first element `True` meaning no cooldown is imposed, the second element of the tuple will
        | be `None`.

        """

        if interaction.command is None and command_name is None:
            raise UnkownCooldownCommand("Couldn't determine command name.")

        command = command_name or interaction.command.name  # pyright:ignore[reportOptionalMemberAccess]
        primary_context = CoolDown._get_context(
            bucket_type=bucket_type, interaction=interaction
        )
        current = datetime.datetime.now()

        try:
            cooldown = CoolDown.cooldown_data[bucket_type][command][
                primary_context
            ]
        except KeyError:
            return (True, None)

        if current > cooldown:
            try:
                del CoolDown.cooldown_data[bucket_type][command][
                    primary_context
                ]
            except KeyError:
                pass
            finally:
                return (True, None)

        else:
            cooldown = CoolDown.cooldown_data[bucket_type][command][
                primary_context
            ]

            if cooldown_return == "datetime":
                return (False, cooldown)

            cooldown_text = f"<t:{round(cooldown.timestamp())}:R>"
            return (False, cooldown_text)

    @staticmethod
    def reset(
        interaction: Interaction,
        bucket_type: CoolDownBucket,
        command_name: Optional[str] = None,
    ) -> bool:
        """Removes the cool down from the bucket type.

        Parameters
        ----------
        interaction
            | The interaction object associated with the command.
        bucket_type
            | The bucket type on which the cooldown should act upon.
        command_name
            | An optional command name to give. This will be choosen over `interaction.command.name` if given.
        """

        if interaction.command is None and command_name is None:
            raise UnkownCooldownCommand("Couldn't determine command name.")

        command = command_name or interaction.command.name  # pyright:ignore[reportOptionalMemberAccess]
        primary_context = CoolDown._get_context(
            bucket_type=bucket_type, interaction=interaction
        )

        try:
            del CoolDown.cooldown_data[bucket_type][command][primary_context]
            return True
        except KeyError:
            return False
