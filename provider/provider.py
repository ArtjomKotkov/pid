from __future__ import annotations

from typing import Type, TypeVar, Any, Optional, Generic

from core import Core
from provider import ProvidedUnit
from resolver import ResolveUnit

T = TypeVar('T')


class Provider(Generic[T], ProvidedUnit, ResolveUnit):
    def __init__(
        self,
        class_: Type[T],
        providers: Optional[list[Provider]] = None,
    ) -> None:
        super().__init__()

        self._class = class_
        self._providers = providers or []

        self._core = Core()
        self._core.remember_dependency(self)

        self._dependency_map: dict[str, str] = {}

        self._make_providers_map()

    def _make_providers_map(self) -> None:
        init_method = self._class.__init__

        try:
            init_annotations = init_method.__annotations__
        except AttributeError:
            return

        self._dependency_map = {provider_name: key for provider_name, key in init_annotations.items()}

    def provide(self, dependencies: dict[str, Any]) -> T:
        return self._class(**dependencies)

    @property
    def class_object(self) -> T:
        return self._class

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def dependencies(self) -> dict[str, str]:
        return self._dependency_map

    @property
    def providers(self) -> list[Provider]:
        return self._providers
