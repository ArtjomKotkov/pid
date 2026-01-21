from __future__ import annotations

from typing import Any, Callable, Type, Optional


__all__ = [
    'IProvider',
    'IModule',
    'IMetaData',
]


class IProvider[T]:
    class_: Any

    is_module: bool
    name: str

    resolve: Callable[[Optional[Any]], T]
    set_providers_pool: Callable

    provider_method: Callable[[*Any], T]
    factory: Callable[[*Any], T]


class IModule[T](IProvider[T]):
    make_exports: Callable
    make_export_providers_pool: Callable


class IMetaData[T]:
    class_: Type[T]
    is_module: bool
    imports: list[Any]
    exports: list[Any]
    providers: list[Any]

    name: str

    make_providable: Callable[[], IProvider]

