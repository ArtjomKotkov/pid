from __future__ import annotations

from typing import Callable, Any, get_type_hints


class ProvidedUnit:
    _class: Any

    is_module: bool
    name: str
    tag: str

    provide: Callable

    @property
    def dependencies(self) -> dict[str, ProvidedUnit]:
        init_method = self._class.__init__

        try:
            init_annotations = get_type_hints(init_method)
        except AttributeError:
            return {}

        return {key: provider for key, provider in init_annotations.items()}
