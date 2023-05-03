from __future__ import annotations

from typing import Type, TypeVar, Optional, Any

from dependency_pool import DependencyPool
from dependency_pool.pool import SharedDependencyPool
from provider import Provider
from resolver import DependencyResolver, ResolveUnit


T = TypeVar('T')


class PidModule(Provider[T], ResolveUnit):
    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[PidModule]] = None,
        exports: Optional[list[Provider]] = None,
        providers: Optional[list[Provider]] = None,
    ) -> None:
        super().__init__(class_)

        self._imports = imports or []
        self._exports = exports or []
        self._providers = providers or []
        self._bound_providers()

        self._inherited_providers = []

        self._pool = DependencyPool(shared_dependencies=self._exports)
        self._shared_pool = SharedDependencyPool()

        self._resolver = DependencyResolver(
            self._pool,
            self._shared_pool,
        )

    def _bound_providers(self) -> None:
        for provider in self._providers:
            provider.bound(self)

    def resolve(self, tag: Optional[str] = None) -> T:
        if resolved_module := self._pool.get(self.name, tag):
            return resolved_module

        try:
            for module in self._imports:
                module.resolve(tag)
                self._shared_pool.merge(module._shared_pool)

            for provider in self._providers:
                self._resolver.resolve(
                    provider,
                    self._providers,
                    own_providers=self._providers,
                    parent=self,
                    tag=tag
                )

            self._shared_pool.fill_from_main_pool(self._pool)

            return self._resolver.resolve(
                self,
                self._providers,
                own_providers=self._providers,
                tag=tag
            )
        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def provide_child(self, name: str, tag: Optional[str] = None) -> Any:
        return self._pool.get(name, tag)

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def providers(self) -> list[Provider]:
        return self._providers

    @property
    def exports(self) -> list[Provider]:
        return self._exports

    @property
    def imports(self) -> list[Provider]:
        return self._imports
