__version__ = "0.1"


import inspect
from discord import Color, Colour
from typing import Optional, TypeAlias, Union, Callable
from enum import StrEnum

TypeColor: TypeAlias = Union[int, Colour, Color]
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


class _ClassPropertyMetaClass(type):
    def __setattr__(self, key, value):
        if key in self.__dict__:
            obj = self.__dict__.get(key)
        if obj and type(obj) is _ClassPropertyDescriptor:
            return obj.__set__(self, value)

        return super(_ClassPropertyMetaClass, self).__setattr__(key, value)


class UtilConfig(metaclass=_ClassPropertyMetaClass):
    _MAIN_COLOR: Optional[TypeColor] = None
    _SUCCESS_COLOR: Optional[TypeColor] = None
    _ERROR_COLOR: Optional[TypeColor] = None
    _FOOTER_TEXT: Optional[str] = None
    _GREEN_CHECK: Optional[str] = None
    _AVATAR_URL: Optional[str] = None
    _VERSION: Optional[str] = None
    _BUG_REPORT_CHANNEL: Optional[int] = None

    @staticmethod
    def __validator(val, typ) -> None:
        if not isinstance(val, typ):
            raise AttributeError(f"Invalid type passed. Expected: {typ}, got {type(val)} instead.")

    @_classproperty
    def MAIN_COLOR(cls) -> Optional[TypeColor]:
        return cls._MAIN_COLOR
    
    @MAIN_COLOR.setter
    def MAIN_COLOR(cls, value: TypeColor) -> None:
        UtilConfig.__validator(value, TypeColor)
        cls._MAIN_COLOR = value

class CogEnum(StrEnum):
    ERROR_HANDLER: str = _BASE_COG_PATH + "worker/error_handler"
    STATUS_HANDLER: str = _BASE_COG_PATH + "worker/status_handler"


UtilConfig.MAIN_COLOR = "dsa"
print(UtilConfig.MAIN_COLOR)