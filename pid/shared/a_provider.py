from __future__ import annotations

from typing import TypeVar, Generic, Any, Callable


T = TypeVar('T')


class IProvider(Generic[T]):
    _class: Any

    is_module: bool
    name: str

    resolve: Callable