from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any, get_type_hints

from bootstrap.utils import get_metadata
from dependency_pool import DependencyPool, UnknownDependency
from shared import IProvider
from shared.exceptions import CannotResolveDependency


T = TypeVar('T')


class Provider(IProvider[T]):
    is_module = False

    def __init__(
        self,
        class_: Type[T],
        providers: Optional[list[Type[T]]] = None,
        factory: Optional[Callable[[*Type[Provider]], T]] = None
    ):
        super().__init__()

        self._class = class_
        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable() for provider_ in providers
        ] if providers else []

        self._factory = factory

        self._pool = DependencyPool()

    @classmethod
    def from_class_metadata(cls, class_: Any) -> Provider:
        metadata = get_metadata(class_)

        return Provider(
            class_=class_,
            providers=metadata.providers,
        )

    def resolve(
        self,
        inherit_pool: Optional[DependencyPool] = None,
        available_providers: Optional[list[IProvider]] = None,
        tag: Optional[str] = None,
    ) -> T:
        try:
            if not available_providers:
                available_providers = []

            if not inherit_pool:
                inherit_pool = DependencyPool()

            return self._resolve(inherit_pool, available_providers, tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        inherit_pool: DependencyPool,
        available_providers: list[IProvider],
        tag: str,
    ) -> T:
        updated_available_providers = [*available_providers, *self._providers]

        inherit_pool_without_providers = inherit_pool.exclude_dependencies(self._providers)

        for provider in self._providers:
            resolved_provider = self._pool.get(provider, tag)

            if resolved_provider is not UnknownDependency:
                continue

            self_pool_copy = self._pool.copy()
            self_pool_copy.merge(inherit_pool_without_providers)

            resolved_provider = provider.resolve(self_pool_copy, updated_available_providers, tag)

            self._pool.merge(self_pool_copy)
            self._pool.add(provider, resolved_provider, tag)

        dependencies = self._prepare(inherit_pool, updated_available_providers, tag)
        resolved_provider = self._provide(dependencies)

        inherit_pool.merge(self._pool.exclude_dependencies(self._providers))

        return resolved_provider

    def _prepare(
        self,
        inherit_pool: DependencyPool,
        available_providers: list[IProvider],
        tag: str,
    ) -> dict[str, Any]:
        provider_dependencies = self.dependencies

        dependencies = {}
        for key, provider in provider_dependencies.items():
            resolved_dependency = self._pool.get(provider, tag)

            if resolved_dependency is UnknownDependency:
                resolved_dependency = inherit_pool.get(provider, tag)

            if resolved_dependency is UnknownDependency:
                provider = next((av_provider for av_provider in available_providers if provider.name == av_provider.name), None)

                if provider is None:
                    raise CannotResolveDependency(f'[{self.name}] {key}')

                resolved_dependency = provider.resolve(inherit_pool, available_providers, tag)
                self._pool.add(provider, resolved_dependency, tag)

            dependencies[key] = resolved_dependency

        for key, resolved_dep in dependencies.items():
            if resolved_dep is UnknownDependency:
                raise CannotResolveDependency(f'[{self.name}] {key}')

        return dependencies

    def _provide(self, dependencies: dict[str, Any]) -> T:
        if self._factory is None:
            return self._class(**dependencies)
        else:
            return self._factory(**dependencies)

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