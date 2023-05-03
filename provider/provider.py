from typing import Type, TypeVar, Any, Optional, Generic
from core import Core
from provider import ProvidedUnit
from resolver import ResolveUnit


T = TypeVar('T')


class Provider(Generic[T], ProvidedUnit, ResolveUnit):
    def __init__(
        self,
        class_: Type[T],
    ) -> None:
        super().__init__()

        self._class = class_

        self._core = Core()
        self._core.remember_dependency(self)

        self._dependency_map: dict[str, str] = {}
        self._owner: Optional[Any] = None

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

    def resolve(self, tag: Optional[str] = None) -> T:
        assert self._owner is not None, 'Provider is out of scope any modules and theirs resolvers.'

        self._owner.resolve(tag)

        return self._owner.provide_child(self.name, tag)

    def bound(self, owner: any) -> None:
        self._owner = owner

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def unresolved_dependencies(self) -> dict[str, str]:
        return self._dependency_map

    @property
    def dependencies(self) -> dict[str, str]:
        return self._dependency_map

    def __repr__(self) -> str:
        return f'Provider - {self.name}'
