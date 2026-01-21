from typing import NamedTuple, Optional, Type, Any


__all__ = [
    'Dependency',
    'ResolveTreeMetadata',
]


class Dependency(NamedTuple):
    raw: bool
    marker: Type[Any]


class ResolveTreeMetadata(NamedTuple):
    chain: list[Any]
