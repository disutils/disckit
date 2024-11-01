from __future__ import annotations

import inspect
from discord import Colour
from typing import Optional, TypeAlias, Union, Callable, Any, Type
from enum import StrEnum

TypeColor: TypeAlias = Union[int, Colour]
_BASE_COG_PATH: str = "disutils/cogs/"


class _ClassPropertyDescriptor:
    def __init__(self, fget: Callable, fset: Optional[Callable] = None) -> None:
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
    _MAIN_COLOR: Optional[TypeColor] = None
    _SUCCESS_COLOR: Optional[TypeColor] = None
    _ERROR_COLOR: Optional[TypeColor] = None
    _FOOTER_TEXT: Optional[str] = None
    _GREEN_CHECK: Optional[str] = None
    _AVATAR_URL: Optional[str] = None
    _VERSION: Optional[str] = None
    _BUG_REPORT_CHANNEL: Optional[int] = None

    @staticmethod
    def __validator(val: Any, typ: Any) -> None:
        if not isinstance(val, typ):
            raise TypeError(
                f"Invalid type passed. Expected: {typ}, got {type(val)} instead."
            )

    @_classproperty
    def MAIN_COLOR(cls: Type[UtilConfig]) -> Optional[TypeColor]:
        return cls._MAIN_COLOR

    @MAIN_COLOR.setter
    def MAIN_COLOR(cls: Type[UtilConfig], value: Optional[TypeColor]) -> None:
        UtilConfig.__validator(value, Optional[TypeColor])
        cls._MAIN_COLOR = value

    @_classproperty
    def SUCCESS_COLOR(cls: Type[UtilConfig]) -> Optional[TypeColor]:
        return cls._SUCCESS_COLOR

    @SUCCESS_COLOR.setter
    def SUCCESS_COLOR(cls: Type[UtilConfig], value: Optional[TypeColor]) -> None:
        UtilConfig.__validator(value, Optional[TypeColor])
        cls._MAIN_COLOR = value

    @_classproperty
    def ERROR_COLOR(cls: Type[UtilConfig]) -> Optional[TypeColor]:
        return cls._ERROR_COLOR

    @ERROR_COLOR.setter
    def ERROR_COLOR(cls: Type[UtilConfig], value: Optional[TypeColor]) -> None:
        UtilConfig.__validator(value, Optional[TypeColor])
        cls._ERROR_COLOR = value

    @_classproperty
    def GREEN_CHECK(cls: Type[UtilConfig]) -> Optional[str]:
        return cls._GREEN_CHECK

    @GREEN_CHECK.setter
    def GREEN_CHECK(cls: Type[UtilConfig], value: Optional[str]) -> None:
        print(__annotations__(value))
        UtilConfig.__validator(value, Optional[str])
        cls._GREEN_CHECK = value

    @_classproperty
    def AVATAR_URL(cls: Type[UtilConfig]) -> Optional[str]:
        return cls._AVATAR_URL

    @AVATAR_URL.setter
    def AVATAR_URL(cls: Type[UtilConfig], value: Optional[str]) -> None:
        UtilConfig.__validator(value, Optional[str])
        cls._AVATAR_URL = value

    @_classproperty
    def VERSION(cls: Type[UtilConfig]) -> Optional[str]:
        return cls._VERSION

    @VERSION.setter
    def VERSION(cls: Type[UtilConfig], value: Optional[str]) -> None:
        UtilConfig.__validator(value, Optional[str])
        cls._VERSION = value

    @_classproperty
    def BUG_REPORT_CHANNEL(cls: Type[UtilConfig]) -> Optional[int]:
        return cls.BUG_REPORT_CHANNEL

    @BUG_REPORT_CHANNEL.setter
    def BUG_REPORT_CHANNEL(cls: Type[UtilConfig], value: Optional[int]) -> None:
        UtilConfig.__validator(value, Optional[int])
        cls._BUG_REPORT_CHANNEL = value


class CogEnum(StrEnum):
    ERROR_HANDLER: str = _BASE_COG_PATH + "worker/error_handler"
    STATUS_HANDLER: str = _BASE_COG_PATH + "worker/status_handler"
