from __future__ import annotations

from typing import Any


class ResolvePool[T]:
    def __init__(self):
        self._dependencies: list[T] = []

    def add(self, resolved_dependency: Any) -> None:
        self._dependencies.append(resolved_dependency)

    def get(self) -> Any:
        return self._dependencies
