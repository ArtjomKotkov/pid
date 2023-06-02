from __future__ import annotations

from typing import Any

from ..shared import IProvider, merge_deep, IMetaData


class ProvidersPool:
    def __init__(self):
        self._providers = dict()

    def add(self, provider: IProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, provider: IProvider) -> Any:
        return self._providers.get(provider.name)

    def get_all(self) -> dict[str, IProvider]:
        return self._providers

    def get_by_metadata(self, metadata: IMetaData) -> Any:
        return self._providers.get(metadata.name)

    def set(self, dependencies: dict[str, Any]) -> None:
        self._providers.clear()
        self._providers.update(dependencies)

    def has_strict(self, provider: IProvider) -> bool:
        return provider is self._providers.get(provider.name)

    def has(self, provider: IProvider) -> bool:
        return bool(self._providers.get(provider.name))

    def has_by_metadata(self, metadata: IMetaData) -> bool:
        return bool(self._providers.get(metadata.name))

    def merge(self, pool: ProvidersPool) -> ProvidersPool:
        self.set(merge_deep(self.providers, pool.providers))

        return self

    def copy(self) -> ProvidersPool:
        new_pool = ProvidersPool()
        new_pool.set(self._providers)

        return new_pool

    @classmethod
    def from_providers(cls, providers: list[IProvider]) -> ProvidersPool:
        new_pool = ProvidersPool()
        for provider in providers:
            new_pool.add(provider)
        return new_pool

    @property
    def providers(self) -> dict[str, Any]:
        return self._providers
