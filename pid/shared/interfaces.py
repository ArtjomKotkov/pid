from __future__ import annotations

from typing import TypeVar, Generic, Any, Callable, Optional, Type

T = TypeVar('T')


__all__ = [
    'IProvider',
    'IModule',
    'IMetaData',
]


class IProvider(Generic[T]):
    _class: Any

    is_module: bool
    name: str

    resolve: Callable[[Optional[str]], T]
    resolve_child: Callable[[IProvider, Optional[str]], T]
    set_providers_pool: Callable


class IModule(Generic[T]):
    _class: Any

    is_module: bool
    name: str

    resolve: Callable
    make_exports: Callable
    make_export_providers_pool: Callable


class IMetaData:
    class_: Type[T]
    is_module: bool
    imports: list[Any]
    exports: list[Any]
    providers: list[Any]

    name: str

    make_providable: Callable[[], IProvider]
