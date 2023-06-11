from typing import NamedTuple, Optional, Type, Any


__all__ = [
    'Dependency',
    'PidTag',
    'ResolveTag',
]


class Dependency(NamedTuple):
    raw: bool
    marker: Type[Any]


class PidTag(str): ...


ResolveTag = Optional[PidTag]
