from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import IProvider, ResolveTag, PidTag, BootstrapMetaData
from ..abstract import AbstractProvider


T = TypeVar('T')


class Provider(AbstractProvider[T]):
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

        self._resolve_pool = ResolvePool()
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def set_providers_pool(self, pool: ProvidersPool) -> None:
        self._inherit_providers_pool = pool

    def resolve(
        self,
        tag: ResolveTag = None,
        bmeta: BootstrapMetaData = None,
    ) -> T:
        if self.class_ == PidTag:
            return tag

        return super().resolve(tag, bmeta)

    def _resolve(
        self,
        tag: ResolveTag = None,
        bmeta: BootstrapMetaData = None,
    ) -> T:
        bmeta.chain.append(self.class_.__name__)

        cached_dependency = self._get_cached_dependency(tag)
        if cached_dependency is not Unknown:
            return cached_dependency

        self._initialize_pools()
        resolved_provider = self._resolve_provider(tag, bmeta)
        self._cache_resolved_provider(resolved_provider, tag)

        return resolved_provider

    def _get_cached_dependency(self, tag: ResolveTag) -> T:
        return self._resolve_pool.get(tag)

    def _initialize_pools(self) -> None:
        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

    def _resolve_provider(self, tag: ResolveTag, bmeta: BootstrapMetaData) -> T:
        return self._provide(tag, bmeta)

    def _cache_resolved_provider(self, provider: T, tag: ResolveTag) -> None:
        self._resolve_pool.add(provider, tag)

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
