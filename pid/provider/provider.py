from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any, get_type_hints

from ..bootstrap.i_metadata import IMetaData
from ..bootstrap.utils import get_metadata
from ..dependency_pool import DependencyPool, Unknown, ProvidersPool
from ..shared import IProvider, CannotResolveDependency


T = TypeVar('T')


class Provider(IProvider[T]):
    is_module = False

    def __init__(
        self,
        class_: Type[T],
        owner: Optional[IProvider] = None,
        providers: Optional[list[Type[T]]] = None,
        factory: Optional[Callable[[*Type[Provider]], T]] = None
    ):
        super().__init__()

        self._class = class_

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable(self) for provider_ in providers
        ] if providers else []

        self._factory = factory

        self.owner = owner

        self._pool = DependencyPool()
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def set_providers_pool(self, pool: ProvidersPool) -> None:
        self._inherit_providers_pool = pool

    def resolve(
        self,
        tag: Optional[str] = None,
    ) -> T:
        try:
            return self._resolve(tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        tag: Optional[str] = None,
    ) -> T:
        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

        for provider in self._providers:
            self.resolve_child(provider, tag)

        dependencies = self._prepare(tag)
        resolved_provider = self._provide(dependencies)

        return resolved_provider

    def _prepare(
        self,
        tag: Optional[str] = None,
    ) -> dict[str, Any]:
        provider_dependencies = self.dependencies

        dependencies = {}
        for key, metadata in provider_dependencies.items():
            resolved_dependency = self._pool.get_by_meta_data(metadata, tag)

            if resolved_dependency is not Unknown:
                dependencies[key] = resolved_dependency

            elif self._inherit_providers_pool.has_by_metadata(metadata):
                related_provider = self._inherit_providers_pool.get_by_metadata(metadata)

                dependencies[key] = related_provider.owner.resolve_child(related_provider, tag)
            else:
                raise CannotResolveDependency(f'[{self.name}] {key}')

        return dependencies

    def _provide(self, dependencies: dict[str, Any]) -> T:
        if self._factory is None:
            return self._class(**dependencies)
        else:
            return self._factory(**dependencies)

    def resolve_child(self, provider: IProvider, tag: Optional[str] = None) -> Any:
        resolved_provider = self._pool.get(provider, tag)

        if resolved_provider is not Unknown:
            return resolved_provider

        resolved_provider = provider.resolve(tag)

        self._pool.add(provider, resolved_provider, tag)

        return resolved_provider

    def _make_own_providers_pool(self) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider)

        return pool

    def _make_child_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.copy().merge(self._own_providers_pool)

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def dependencies(self) -> dict[str, IMetaData]:
        method = self._class.__init__ if self._factory is None else self._factory

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: get_metadata(class_)
            for key, class_
            in init_annotations.items()
        }
