from __future__ import annotations

from typing import Type, TypeVar, Optional, Callable, Any

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import IProvider, ResolveTag, PidTag
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
    ) -> T:
        if self.class_ == PidTag:
            return tag

        return super().resolve(tag)

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

        resolved_provider = self._provide(tag)

        self._resolve_pool.add(resolved_provider, tag)

        return resolved_provider

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
