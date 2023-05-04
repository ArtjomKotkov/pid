from __future__ import annotations

from typing import Type, TypeVar, Any, Optional, Generic

from core import Core
from dependency_pool import DependencyPool, UnknownDependency
from exceptions import CannotResolveDependency
from provider import ProvidedUnit
from resolver import ResolveUnit

T = TypeVar('T')


class ProviderWrapper(ResolveUnit):
    def __init__(
        self,
        provider: ProvidedUnit
    ) -> None:
        super().__init__()

        self._provider = provider

        self._owner: Optional[Any] = None

        self._core = Core()

        self._pool = DependencyPool()

    # def _resolve(self, tag: Optional[str] = None) -> T:
    #     resolved_inner_dependencies = {}
    #     for key, dep_name in self._provider.dependencies.items():
    #         core_unit = self._core.get(dep_name)
    #
    #         resolved_inner_dependencies[key] = (
    #             ProviderWrapper(core_unit.dependency)._resolve(tag)
    #             if not core_unit.request_unresolved
    #             else core_unit.dependency
    #         )
    #
    #         self._inherited_pool.merge(resolved_inner_dependencies[key]._shared_pool)
    #
    #     provided_dependency = self._provider.provide(**resolved_inner_dependencies)
    #     self._shared_pool = self._pool.exclude_dependencies(self._provider.providers)
    #
    #     return provided_dependency
    #
    # def resolve(self, tag: Optional[str] = None) -> T:
    #     assert self._owner is not None, 'Provider is out of scope any modules and theirs resolvers.'
    #
    #     self._owner.resolve(tag)
    #
    #     return self._owner.provide_child(self.name, tag)

    def resolve(
        self,
        module_node_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        resolved_provider = self._pool.get(self.name, tag)

        if not isinstance(resolved_provider, UnknownDependency):
            return resolved_provider

        try:
            if not module_node_pool:
                module_node_pool = DependencyPool()

            return self._resolve(module_node_pool, tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        inherited_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        providers = self._provider.providers

        for provider in providers:
            if not self._can_resolve_provider(provider, inherited_pool, tag):
                raise CannotResolveDependency()

            provider.resolve(inherited_pool, tag)

            self._pool.merge(provider._pool.exclude_dependencies(providers))

        return self._provide(inherited_pool, tag)

    def _provide(
        self,
        inherited_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        provider_dependencies = self._provider.dependencies

        dependencies = {
            key: self._pool.get(dep_name, tag) or inherited_pool.get(dep_name, tag)
            for key, dep_name
            in provider_dependencies.items()
        }

        for key, resolved_dep in dependencies.items():
            if resolved_dep is None:
                raise CannotResolveDependency(f'[{self.name}] {key} - {resolved_dep}')

        provided_dependency = self._provider.provide(dependencies)
        self._pool.add(self.name, provided_dependency, tag)
        inherited_pool.merge(self._pool.exclude_dependencies(provider_dependencies))

        return provided_dependency

    def _can_resolve_provider(
        self,
        provider: ProvidedUnit,
        inherited_pool: DependencyPool,
        tag: Optional[str] = None
    ) -> bool:
        return inherited_pool.has(provider.name, tag)

    def bound(self, owner: any) -> None:
        self._owner = owner

    @property
    def name(self) -> str:
        return self._provider.name
