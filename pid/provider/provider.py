from __future__ import annotations

from typing import Type, Optional, Callable, Any

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import IProvider, ResolveTreeMetadata
from ..abstract import AbstractProvider


class Provider[T](AbstractProvider[T]):
    is_module = False

    def __init__(
        self,
        class_: Type[T],
        providers: Optional[list[Type[T]]] = None,
        factory: Optional[Callable[[*Type[Provider]], T]] = None
    ):
        super().__init__()

        self.class_ = class_

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable() for provider_ in providers
        ] if providers else []

        self._factory = factory

        self._resolved_provider: Optional[T] = None
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def set_providers_pool(self, pool: ProvidersPool) -> None:
        self._inherit_providers_pool = pool

    def resolve(
        self,
        resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> T:
        resolve_tree_metadata = resolve_tree_metadata or ResolveTreeMetadata([])

        return super().resolve(resolve_tree_metadata)

    def _resolve(
        self,
        resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> T:
        resolve_tree_metadata.chain.append(self.class_.__name__)

        if self._resolved_provider:
            return self._resolved_provider

        self._initialize_pools()
        resolved_provider = self._provide(resolve_tree_metadata)
        self._resolved_provider = resolved_provider
        return self._resolved_provider


    def _initialize_pools(self) -> None:
        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

    def _make_own_providers_pool(self) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider)

        return pool

    def _make_child_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.copy().merge(self._own_providers_pool)

    @property
    def provider_method(self) -> Callable[[*Any], T]:
        return self.class_.__init__ if self._factory is None else self._factory
