from __future__ import annotations

from typing import Any, get_type_hints, get_origin, get_args, Callable, Optional

from ..pools import ProvidersPool
from ..shared import IProvider, Dependency, CannotResolveDependency, ResolveTreeMetadata


class AbstractProvider[T](IProvider[T]):
    _own_providers_pool: ProvidersPool
    _inherit_providers_pool: ProvidersPool
    _factory: Optional[Callable[[*Any], T]]

    def resolve(
            self,
            resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> T:
        return self._resolve(resolve_tree_metadata)

    def _resolve(self, resolve_tree_metadata: ResolveTreeMetadata = None) -> T:
        raise NotImplementedError

    def _prepare(
            self,
            resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> dict[str, Any]:
        dependencies = {}

        for key, dependency in self.dependencies.items():
            provider = self._get_provider_from_pools(dependency.marker, key, resolve_tree_metadata)

            if dependency.raw:
                dependencies[key] = provider
            else:
                dependencies[key] = provider.resolve(resolve_tree_metadata)

        return dependencies

    def _get_provider_from_pools(
            self,
            marker: Any,
            dependency_key: str,
            resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> Any:
        if self._own_providers_pool.has(marker):
            return self._own_providers_pool.get(marker)
        elif self._inherit_providers_pool.has(marker):
            return self._inherit_providers_pool.get(marker)
        else:
            chain_str = "\n".join(
                '\t' * i + f'^- {elem}' for i, elem in enumerate(reversed(resolve_tree_metadata.chain)))

            raise CannotResolveDependency(
                f'Error while trying resolving dependency:\n'
                f'{self.name}(..., {dependency_key}={marker!r}, ...)\n'
                f'{chain_str}'
            )

    def _provide(self, resolve_tree_metadata: ResolveTreeMetadata = None) -> T:
        dependencies = self._prepare(resolve_tree_metadata)
        return self.factory(**dependencies)

    @property
    def factory(self) -> Callable[[*Any], T]:
        if self.is_module:
            return self.class_
        elif self._factory is None:
            return self.class_
        else:
            return self._factory

    @property
    def name(self) -> str:
        return self.class_.__name__

    @property
    def dependencies(self) -> dict[str, Dependency]:
        try:
            init_annotations = get_type_hints(self.provider_method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        result = {}
        for key, annotation in init_annotations.items():
            origin = get_origin(annotation)
            if origin and issubclass(origin, AbstractProvider):
                result[key] = Dependency(
                    marker=get_args(annotation)[0],
                    raw=True,
                )
                continue

            result[key] = Dependency(
                marker=annotation,
                raw=False
            )

        return result
