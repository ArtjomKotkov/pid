from __future__ import annotations

from typing import Type, Generic, TypeVar, Optional

from pid_types import ProvidersType
from provider import Provider
from resolver import DependencyResolver


T = TypeVar('T')


class PidModule(Generic[T], Provider):
    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[PidModule]] = None,
        exports: Optional[ProvidersType] = None,
        providers: Optional[ProvidersType] = None,
    ) -> None:
        super().__init__(class_)

        self._imports = imports or []
        self._exports = exports or []
        self._providers = providers or []

        self._resolver = DependencyResolver()

    @property
    def name(self) -> str:
        return self._class.__name__

    def inherit(self, providers: ProvidersType) -> None:
        self._providers.extend(providers)

    def resolve(self) -> T:
        for provider in self._providers:
            self._resolver.resolve(provider, self.available_providers, parent=self)

        for module in self._imports:
            module.inherit(self._exports)
            module.resolve()

        return self._resolver.resolve(self, self.available_providers, is_module=True)

    @property
    def providers(self) -> ProvidersType:
        return self._providers

    @property
    def exports(self) -> ProvidersType:
        return self._exports

    @property
    def available_providers(self) -> ProvidersType:
        providers = set(self.providers)
        for module in self._imports:
            providers.update(module.exports)

        return list(providers)


