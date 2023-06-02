from typing import NamedTuple

from ..shared import IMetaData


__all__ = [
    'Dependency',
    'PidTag',
]


class Dependency(NamedTuple):
    metadata: IMetaData
    raw: bool


class PidTag(str): ...
