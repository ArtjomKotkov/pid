from __future__ import annotations

from typing import TypeVar, Generic, Any, Callable, Optional

T = TypeVar('T')


class IProvider(Generic[T]):
    _class: Any

    is_module: bool
    name: str

    resolve: Callable[[Optional[str]], T]
    set_providers_pool: Callable


class IModule(Generic[T]):
    _class: Any

    is_module: bool
    name: str

    resolve: Callable
    make_exports: Callable
    make_export_providers_pool: Callable
