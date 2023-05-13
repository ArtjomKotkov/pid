from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any, get_type_hints

from bootstrap.utils import get_metadata
from dependency_pool import DependencyPool, UnknownDependency, ProvidersPool
from shared import IProvider
from shared.exceptions import CannotResolveDependency


T = TypeVar('T')


class Provider(IProvider[T]):
    is_module = False

    def __init__(
        self,
        class_: Type[T],
        owner: IProvider,
        providers: Optional[list[Type[T]]] = None,
        factory: Optional[Callable[[*Type[Provider]], T]] = None
    ):
        super().__init__()

        self._class = class_

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable() for provider_ in providers
        ] if providers else []

        self._factory = factory

        self._owner = owner

        self._pool = DependencyPool()
        self._inherit_providers_pool = ProvidersPool()

    @classmethod
    def from_class_metadata(cls, class_: Any, owner: IProvider) -> Provider:
        metadata = get_metadata(class_)

        return Provider(
            class_=class_,
            providers=metadata.providers,
            owner=owner,
        )

    def resolve(
        self,
        inherit_providers_pool: ProvidersPool,
        tag: Optional[str] = None,
    ) -> T:
        try:
            self._inherit_providers_pool = inherit_providers_pool

            return self._resolve(inherit_providers_pool, tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        tag: str,
    ) -> T:
        for provider in self._providers:
            self.resolve_child(provider, tag)

        dependencies = self._prepare(tag)
        resolved_provider = self._provide(dependencies)

        return resolved_provider

    def _prepare(
        self,
        tag: str,
    ) -> dict[str, Any]:
        provider_dependencies = self.dependencies

        dependencies = {}
        for key, provider in provider_dependencies.items():
            dependencies[key] = self._pool.get(provider, tag)

        for key, resolved_dep in dependencies.items():
            if resolved_dep is UnknownDependency:
                raise CannotResolveDependency(f'[{self.name}] {key}')

        return dependencies

    def _provide(self, dependencies: dict[str, Any]) -> T:
        if self._factory is None:
            return self._class(**dependencies)
        else:
            return self._factory(**dependencies)

    def resolve_child(self, provider: IProvider, tag: Optional[str] = None) -> Any:
        own_providers_pool = self._make_own_providers_pool(tag)
        child_providers_pool = self._inherit_providers_pool.copy().merge(own_providers_pool)

        if not child_providers_pool.has_strict(provider, tag):
            raise CannotResolveDependency()

        resolved_provider = self._pool.get(provider, tag)

        if resolved_provider is not UnknownDependency:
            return resolved_provider

        resolved_provider = provider.resolve(
            child_providers_pool,
            tag,
        )

        self._pool.add(provider, resolved_provider, tag)

        return resolved_provider

    def _make_own_providers_pool(self, tag: Optional[str] = None) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider, tag)

        return pool

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def dependencies(self) -> dict[str, IProvider]:
        method = self._class.__init__ if self._factory is None else self._factory

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: get_metadata(class_).make_providable()
            for key, class_
            in init_annotations.items()
        }