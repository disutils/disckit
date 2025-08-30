"""
Disutils' utility package
~~~~~~~~~~~~~~~~~~~~~~~~~

A utility package made for the disutils bots.

:copyright: (c) 2024-present Disutils Team
:license: MIT, see LICENSE for more details.
"""

__version__ = "1.1.4"
__title__ = "disckit"
__author__ = "Jiggly Balls"
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Disutils Team"

from typing import Literal, NamedTuple

from disckit.config import CogEnum, UtilConfig

__all__ = ("UtilConfig", "CogEnum", "version_info")


class _VersionInfo(NamedTuple):
    major: str
    minor: str
    patch: str
    release_level: Literal["alpha", "beta", "final"]


def _expand() -> _VersionInfo:
    v = __version__.split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level = level_types.get(v[-1], "final")
    return _VersionInfo(
        major=v[0],
        minor=v[1],
        patch=v[2],
        release_level=level,  # pyright:ignore[reportArgumentType]
    )


version_info: _VersionInfo = _expand()
