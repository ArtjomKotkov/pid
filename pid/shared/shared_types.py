from typing import NamedTuple, Optional, Type, Any


__all__ = [
    'Dependency',
    'PidTag',
    'ResolveTag',
    'BootstrapMetaData',
]


class Dependency(NamedTuple):
    raw: bool
    marker: Type[Any]


class PidTag(str): ...


ResolveTag = Optional[PidTag]


class BootstrapMetaData(NamedTuple):
    chain: list[Any]
