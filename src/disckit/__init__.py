"""
Disutils' utility package
~~~~~~~~~~~~~~~~~~~~~~~~~

A utility package made for the disutils bots.

:copyright: (c) 2024-present Disutils Team
:license: MIT, see LICENSE for more details.

"""

__version__ = "0.5"
__title__ = "disckit"
__author__ = "Jiggly Balls"
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Disutils Team"

from disckit.config import UtilConfig, CogEnum
from disckit.errors import DisException, CogLoadError
from typing import NamedTuple, Literal

__all__ = ("UtilConfig", "CogEnum", "DisException", "CogLoadError")


class VersionInfo(NamedTuple):
    major: int
    minor: int
    release_level: Literal["alpha", "beta", "final"]


def _expand() -> VersionInfo:
    v = __version__.split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level = level_types.get(v[-1], "final")
    return VersionInfo(major=v[0], minor=v[1], release_level=level)


version_info: VersionInfo = _expand()
