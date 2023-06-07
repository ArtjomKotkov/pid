from __future__ import annotations

from typing import TypeVar, Any, get_type_hints, get_origin, get_args, Callable, Optional

from ..bootstrap.utils import get_metadata
from ..pools import ProvidersPool
from ..shared import IProvider, Dependency, CannotResolveDependency, ResolveTag


T = TypeVar('T')


class AbstractProvider(IProvider[T]):
    _own_providers_pool: ProvidersPool
    _inherit_providers_pool: ProvidersPool
    _factory: Optional[Callable[[*Any], T]]

    def resolve(
        self,
        tag: ResolveTag = None,
    ) -> T:
        return self._resolve(tag)

    def _resolve(self, tag):
        raise NotImplementedError

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

    def _provide(self, tag: ResolveTag = None) -> T:
        dependencies = self._prepare(tag)

        return self.factory(**dependencies)

    @property
    def factory(self) -> Callable[[*Any], T]:
        if self.is_module:
            return self._class
        elif self._factory is None:
            return self._class
        else:
            return self._factory

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def dependencies(self) -> dict[str, Dependency]:
        try:
            init_annotations = get_type_hints(self.provider_method)
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
