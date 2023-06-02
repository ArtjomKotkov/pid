from __future__ import annotations

from typing import Any, Generic, TypeVar

from .pool_types import Unknown

from ..shared import ResolveTag


T = TypeVar('T')


class ResolvePool(Generic[T]):
    def __init__(self):
        self._dependencies: dict[ResolveTag, T] = {}

    def add(self, resolved_dependency: Any, tag: ResolveTag = None) -> None:
        self._dependencies[tag] = resolved_dependency

    def get(self, tag: ResolveTag = None) -> Any:
        return self._dependencies.get(tag, Unknown)
