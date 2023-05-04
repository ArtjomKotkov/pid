from __future__ import annotations

from typing import Type, TypeVar, Optional, Any

from dependency_pool import DependencyPool, UnknownDependency
from dependency_pool.pool import SharedDependencyPool
from exceptions import CannotResolveDependency
from provider import Provider, ProviderWrapper
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
        self._providers = [
            ProviderWrapper(provider)
            for provider
            in providers
        ] or []

        self._pool = DependencyPool()

    def _bound_providers(self) -> None:
        for provider in self._providers:
            provider.bound(self)

    def resolve(
        self,
        node_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        resolved_module = self._pool.get(self.name, tag)

        if not isinstance(resolved_module, UnknownDependency):
            return resolved_module

        if not node_pool:
            node_pool = DependencyPool()

        try:
            for module in self._imports:
                node_pool = DependencyPool()

                module.resolve(node_pool, tag)

                self._pool.merge(node_pool)

            return self._resolve(node_pool, tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        node_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        for provider in self._providers:
            provider.resolve(self._pool, tag)

        node_pool.merge(self._pool.with_dependencies(self._exports))

        return self._provide(tag)

    def _provide(self, tag:  Optional[str] = None) -> T:
        dependencies = {
            key: self._pool.get(dep_name, tag)
            for key, dep_name
            in self.dependency_map.items()
        }

        unknown_dependencies = [
            (key, self.dependency_map[key],)
            for key, dep
            in dependencies.items()
            if isinstance(dep, UnknownDependency)
        ]

        if unknown_dependencies:
            dep_string = '\n'.join([f'{self.name}: {dep_pair[0]} - {dep_pair[1]}' for dep_pair in unknown_dependencies])
            error_msg = '\nCurrent dependencies isn\'t provided in any bounded module.\n' + dep_string

            raise CannotResolveDependency(error_msg)

        return self.provide(dependencies)

    def provide(self, dependencies: dict[str, Any]) -> T:
        return self._class(**dependencies)

    def provide_child(self, name: str, tag: Optional[str] = None) -> Any:
        return self._pool.get(name, tag)

    @property
    def dependency_map(self) -> dict[str, str]:
        init_method = self._class.__init__

        try:
            init_annotations = init_method.__annotations__
        except AttributeError:
            return {}

        return {key: provider_name for key, provider_name in init_annotations.items()}

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
