"""
Disutils' utility package
~~~~~~~~~~~~~~~~~~~~~~~~~

A utility package made for the disutils bots.

:copyright: (c) 2024-present Disutils Team
:license: MIT, see LICENSE for more details.

"""

__version__ = "0.8b"
__title__ = "disckit"
__author__ = "Jiggly Balls"
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Disutils Team"

from typing import Literal, NamedTuple

from disckit.config import CogEnum, UtilConfig
from disckit.errors import CogLoadError, DisException

__all__ = ("UtilConfig", "CogEnum", "DisException", "CogLoadError")


class VersionInfo(NamedTuple):
    major: int
    minor: int
    release_level: Literal["alpha", "beta", "final"]


def _expand() -> VersionInfo:
    v = __version__.split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level: Literal["alpha", "beta", "final"] = level_types.get(v[-1], "final")
    return VersionInfo(major=int(v[0]), minor=int(v[1]), release_level=level)


version_info: VersionInfo = _expand()
