from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any, get_type_hints, get_origin, get_args

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import IProvider, CannotResolveDependency, Dependency, ResolveTag

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

        self._resolve_pool = ResolvePool()
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def set_providers_pool(self, pool: ProvidersPool) -> None:
        self._inherit_providers_pool = pool

    def resolve(
        self,
        tag: ResolveTag = None,
    ) -> T:
        return self._resolve(tag)

    def _resolve(
        self,
        tag: ResolveTag = None,
    ) -> T:
        resolved_dependency = self._resolve_pool.get(tag)
        if resolved_dependency is not Unknown:
            return resolved_dependency

        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

        dependencies = self._prepare(tag)
        resolved_provider = self._provide(dependencies)

        self._resolve_pool.add(resolved_provider, tag)

        return resolved_provider

    def _prepare(
        self,
        tag: ResolveTag = None,
    ) -> dict[str, Any]:
        provider_dependencies = self.dependencies

        dependencies = {}
        for key, dependency in provider_dependencies.items():
            metadata = dependency.metadata

            if not dependency.raw:
                if self._own_providers_pool.has_by_metadata(metadata):
                    related_provider = self._own_providers_pool.get_by_metadata(metadata)

                    dependencies[key] = related_provider.resolve(tag)

                elif self._inherit_providers_pool.has_by_metadata(metadata):
                    related_provider = self._inherit_providers_pool.get_by_metadata(metadata)

                    dependencies[key] = related_provider.resolve(tag)
                else:
                    raise CannotResolveDependency(f'[{self.name}] {key}')

            else:
                if self._own_providers_pool.has_by_metadata(metadata):
                    dependencies[key] = self._own_providers_pool.get_by_metadata(metadata)

                elif self._inherit_providers_pool.has_by_metadata(metadata):
                    dependencies[key] = self._inherit_providers_pool.get_by_metadata(metadata)
                else:
                    raise CannotResolveDependency(f'[{self.name}] {key}')

        return dependencies

    def _provide(self, dependencies: dict[str, Any]) -> T:
        if self._factory is None:
            return self._class(**dependencies)
        else:
            return self._factory(**dependencies)

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
    def dependencies(self) -> dict[str, Dependency]:
        method = self._class.__init__ if self._factory is None else self._factory

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: Dependency(
                metadata=get_metadata(annotation),
                raw=False,
            )

            if not get_origin(annotation) else

            Dependency(
                metadata=get_metadata(get_args(annotation)[0]),
                raw=True,
            )

            for key, annotation
            in init_annotations.items()
        }