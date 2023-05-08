from __future__ import annotations

from typing import get_type_hints, TypeVar, Generic, Any, Callable


T = TypeVar('T')


class AbstractProvider(Generic[T]):
    _class: Any
    is_module: bool
    name: str

    resolve: Callable

    @property
    def dependencies(self) -> dict[str, AbstractProvider]:
        init_method = self._class.__init__

        try:
            init_annotations = get_type_hints(init_method)
        except AttributeError:
            return {}

        return {key: provider for key, provider in init_annotations.items()}