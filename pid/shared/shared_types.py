from typing import NamedTuple, Optional

from ..shared import IMetaData


__all__ = [
    'Dependency',
    'PidTag',
    'ResolveTag',
]


class Dependency(NamedTuple):
    metadata: IMetaData
    raw: bool


class PidTag(str): ...


ResolveTag = Optional[PidTag]
