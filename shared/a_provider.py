from __future__ import annotations

from typing import get_type_hints, TypeVar, Generic, Any, Callable, Optional, Type


T = TypeVar('T')


class AbstractProvider(Generic[T]):
    _class: Any
    _factory: Optional[Callable[[*Type[AbstractProvider]], T]]

    is_module: bool
    name: str

    resolve: Callable

    @property
    def dependencies(self) -> dict[str, AbstractProvider]:
        method = self._class.__init__ if self._factory is None else self._factory

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: provider
            for key, provider
            in init_annotations.items()
        }
