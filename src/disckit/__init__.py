"""
Disutils' utility package
~~~~~~~~~~~~~~~~~~~~~~~~~

A utility package made for the disutils bots.

:copyright: (c) 2024-present Disutils Team
:license: MIT, see LICENSE for more details.
"""

__version__ = "0.9"
__title__ = "disckit"
__author__ = "Jiggly Balls"
__license__ = "MIT"
__copyright__ = "Copyright 2024-present Disutils Team"

from typing import Literal, NamedTuple

from disckit.config import CogEnum, UtilConfig

__all__ = ("UtilConfig", "CogEnum", "version_info")


class _VersionInfo(NamedTuple):
    major: int
    minor: int
    release_level: Literal["alpha", "beta", "final"]


def _expand() -> _VersionInfo:
    v = __version__.split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level: Literal["alpha", "beta", "final"] = level_types.get(
        v[-1][-1], "final"
    )  # type: ignore
    minor_version = v[1] if level == "final" else v[1][0]
    return _VersionInfo(
        major=int(v[0]), minor=int(minor_version), release_level=level
    )


version_info: _VersionInfo = _expand()
