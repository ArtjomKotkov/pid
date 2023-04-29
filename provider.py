from typing import Type, TypeVar, Any
from core import Core

T = TypeVar('T')


class Provider:
    def __init__(
        self,
        class_: Type[T],
    ) -> None:
        self._class = class_

        self._core = Core()
        self._core.remember(self)

        self._dependency_map: dict[str, str] = {}

        self._make_providers_map()

    def _make_providers_map(self) -> None:
        init_method = self._class.__init__

        try:
            init_annotations = init_method.__annotations__
        except AttributeError:
            return

        self._dependency_map = {provider_name: key for provider_name, key in init_annotations.items()}

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def unresolved_dependencies(self) -> dict[str, str]:
        return self._dependency_map

    def provide(self, dependencies: dict[str, Any]) -> T:
        return self._class(**dependencies)

    def __repr__(self) -> str:
        return f'Provider - {self.name}'
