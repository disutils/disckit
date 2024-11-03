from __future__ import annotations

import inspect
from discord import Colour, ActivityType
from typing import (
    Optional,
    TypeAlias,
    Union,
    ClassVar,
    Type,
    Awaitable,
    Tuple,
    List,
    Set,
    Any,
)
from enum import StrEnum
from disckit.utils import default_status_handler

TypeColor: TypeAlias = Union[int, Colour]
_BASE_COG_PATH: str = "disckit.cogs."


class _ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, class_=None):
        if class_ is None:
            class_ = type(obj)
        return self.fget.__get__(obj, class_)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("Can't set attribute.")
        if inspect.isclass(obj):
            type_ = obj
            obj = None
        else:
            type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def _classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return _ClassPropertyDescriptor(func)


class _MetaClassProperty(type):
    def __setattr__(self, key, value):
        if key in self.__dict__:
            obj = self.__dict__.get(key)
        if obj and type(obj) is _ClassPropertyDescriptor:
            return obj.__set__(self, value)

        return super().__setattr__(key, value)


class UtilConfig(metaclass=_MetaClassProperty):
    """The utility class which configures disckit's utilities."""

    _MAIN_COLOR: ClassVar[TypeColor] = 0x5865F2
    _SUCCESS_COLOR: ClassVar[TypeColor] = 0x00FF00
    _ERROR_COLOR: ClassVar[TypeColor] = 0xFF0000
    _SUCCESS_EMOJI: ClassVar[str] = "✅"
    _ERROR_EMOJI: ClassVar[str] = "❌"
    _FOOTER_IMAGE: ClassVar[Optional[str]] = None
    _FOOTER_TEXT: ClassVar[Optional[str]] = None
    _STATUS_FUNC: ClassVar[
        Tuple[Awaitable[Union[Tuple[str, ...], List[str], Set[str]]], Tuple]
    ] = (
        default_status_handler,
        (),
    )
    _STATUS_TYPE: ClassVar[ActivityType] = ActivityType.listening
    _STATUS_COOLDOWN: ClassVar[Optional[int]] = None
    _BUG_REPORT_CHANNEL: ClassVar[Optional[int]] = None

    @staticmethod
    def __validator(val: Any, typ: Any) -> None:
        if not isinstance(val, typ):
            raise TypeError(
                f"Invalid type passed. Expected: {typ}, got {type(val)} instead."
            )

    @_classproperty
    def MAIN_COLOR(cls: Type[UtilConfig]) -> TypeColor:
        """Class Attribute
        ---
        MAIN_COLOR: :class:`Optional[int, discord.color.Color]`

            The color of the MainEmbed.
        """
        return cls._MAIN_COLOR

    @MAIN_COLOR.setter
    def MAIN_COLOR(cls: Type[UtilConfig], value: TypeColor) -> None:
        UtilConfig.__validator(value, TypeColor)
        cls._MAIN_COLOR = value

    @_classproperty
    def SUCCESS_COLOR(cls: Type[UtilConfig]) -> TypeColor:
        """Class Attribute
        ---
        SUCCESS_COLOR: :class:`Optional[int, discord.color.Color]`

            The color of the SuccessEmbed.
        """
        return cls._SUCCESS_COLOR

    @SUCCESS_COLOR.setter
    def SUCCESS_COLOR(cls: Type[UtilConfig], value: TypeColor) -> None:
        UtilConfig.__validator(value, TypeColor)
        cls._MAIN_COLOR = value

    @_classproperty
    def ERROR_COLOR(cls: Type[UtilConfig]) -> TypeColor:
        """Class Attribute
        ---
        ERROR_COLOR: :class:`Optional[int, discord.color.Color]`

            The color of the ErrorEmbed.
        """
        return cls._ERROR_COLOR

    @ERROR_COLOR.setter
    def ERROR_COLOR(cls: Type[UtilConfig], value: TypeColor) -> None:
        UtilConfig.__validator(value, TypeColor)
        cls._ERROR_COLOR = value

    @_classproperty
    def SUCCESS_EMOJI(cls: Type[UtilConfig]) -> str:
        """Class Attribute
        ---
        SUCCESS_EMOJI: :class:`Optional[str]`

            An emoji used in the title of the SuccessEmbed.
        """
        return cls._SUCCESS_EMOJI

    @SUCCESS_EMOJI.setter
    def SUCCESS_EMOJI(cls: Type[UtilConfig], value: str) -> None:
        UtilConfig.__validator(value, str)
        cls._SUCCESS_EMOJI = value

    @_classproperty
    def ERROR_EMOJI(cls: Type[UtilConfig]) -> Optional[str]:
        """Class Attribute
        ---
        ERROR_EMOJI: :class:`Optional[str]`

            An emoji used in the title of the ErrorEmbed.
        """
        return cls._ERROR_EMOJI

    @ERROR_EMOJI.setter
    def ERROR_EMOJI(cls: Type[UtilConfig], value: str) -> None:
        UtilConfig.__validator(value, str)
        cls._ERROR_EMOJI = value

    @_classproperty
    def FOOTER_IMAGE(cls: Type[UtilConfig]) -> Optional[str]:
        """Class Attribute
        ---
        FOOTER_IMAGE: :class:`Optional[str]`

            A URL to an image for the footer of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.
        """
        return cls._FOOTER_IMAGE

    @FOOTER_IMAGE.setter
    def FOOTER_IMAGE(cls: Type[UtilConfig], value: str) -> None:
        UtilConfig.__validator(value, str)
        cls._FOOTER_IMAGE = value

    @_classproperty
    def FOOTER_TEXT(cls: Type[UtilConfig]) -> Optional[TypeColor]:
        """Class Attribute
        ---
        FOOTER_TEXT: :class:`Optional[str]`

            The footer text of `MainEmbed`, `SuccessEmbed` and `ErrorEmbed`.
        """
        return cls._FOOTER_TEXT

    @FOOTER_TEXT.setter
    def FOOTER_TEXT(cls: Type[UtilConfig], value: str) -> None:
        UtilConfig.__validator(value, str)
        cls._FOOTER_TEXT = value

    @_classproperty
    def STATUS_FUNC(
        cls: Type[UtilConfig],
    ) -> Tuple[Awaitable[Union[Tuple, List, Set]], Tuple]:
        """Class Attribute
        ---
        STATUS_FUNC: :class:`Tuple[Awaitable[Union[Tuple, List, Set]], Tuple]`

            A tuple having it's first element as a coroutine object which will
            be awaited when-<br>
            - When the cog first loads.<br>
            - When the handler is done iterating through all statuses returned from the function.<br>
            The second element is a tuple containing the extra arguments that can be passed to your
            custom status handler function. If no arguments has to be passed an empty tuple
            should suffice.
        """
        return cls._STATUS_FUNC

    @STATUS_FUNC.setter
    def STATUS_FUNC(
        cls: Type[UtilConfig], value: Tuple[Awaitable[Union[Tuple, List, Set]], Tuple]
    ) -> None:
        UtilConfig.__validator(value, Tuple[Awaitable[Union[Tuple, List, Set]], Tuple])
        cls._STATUS_FUNC = value

    @_classproperty
    def STATUS_TYPE(cls: Type[UtilConfig]) -> ActivityType:
        """Class Attribute
        ---
        STATUS_TYPE: :class:`ActivityType`

            The discord acitvity type used by the StatusHandler.
        """
        return cls._STATUS_TYPE

    @STATUS_TYPE.setter
    def STATUS_TYPE(cls: Type[UtilConfig], value: ActivityType) -> None:
        UtilConfig.__validator(value, ActivityType)
        cls._STATUS_TYPE = value

    @_classproperty
    def STATUS_COOLDOWN(cls: Type[UtilConfig]) -> Optional[int]:
        """Class Attribute
        ---
        STATUS_COOLDOWN: :class:`Optional[int]`

            A cooldown in seconds for how long a status will play before changing in the `StatusHandler` cog.
        """
        return cls._STATUS_COOLDOWN

    @STATUS_COOLDOWN.setter
    def STATUS_COOLDOWN(cls: Type[UtilConfig], value: int) -> None:
        UtilConfig.__validator(value, int)
        cls._STATUS_COOLDOWN = value

    @_classproperty
    def BUG_REPORT_CHANNEL(cls: Type[UtilConfig]) -> Optional[int]:
        """Class Attribute
        ---
        BUG_REPORT_CHANNEL: :class:`Optional[int]`

            The channel ID to where the bug reports will be sent to by the `ErrorHandler` cog.
        """
        return cls._BUG_REPORT_CHANNEL

    @BUG_REPORT_CHANNEL.setter
    def BUG_REPORT_CHANNEL(cls: Type[UtilConfig], value: int) -> None:
        UtilConfig.__validator(value, int)
        cls._BUG_REPORT_CHANNEL = value


class CogEnum(StrEnum):
    ERROR_HANDLER: str = _BASE_COG_PATH + "worker.error_handler"
    """An extension for error handling."""

    STATUS_HANDLER: str = _BASE_COG_PATH + "worker.status_handler"
    """An extension for the bot's status handling."""
