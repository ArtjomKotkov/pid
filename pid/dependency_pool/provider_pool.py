from __future__ import annotations

from collections import defaultdict
from typing import Optional

from ..bootstrap.i_metadata import IMetaData
from ..shared import IProvider, merge_deep


class ProvidersPool:
    def __init__(self):
        self._providers: dict[str, dict[str, IProvider]] = defaultdict(dict)

    def add(self, provider: IProvider, tag: Optional[str] = None) -> None:
        self._providers[tag][provider.name] = provider

    def get(self, provider: IProvider, tag: Optional[str] = None) -> any:
        return self._providers.get(tag, {}).get(provider.name)

    def get_all(self, tag: Optional[str] = None) -> dict[str, IProvider]:
        return self._providers[tag]

    def get_by_metadata(self, metadata: IMetaData, tag: Optional[str] = None) -> any:
        return self._providers.get(tag, {}).get(metadata.name)

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._providers.clear()
        self._providers.update(dependencies)

    def has_strict(self, provider: IProvider, tag: Optional[str] = None) -> bool:
        return provider is self._providers.get(tag, {}).get(provider.name)

    def has(self, provider: IProvider, tag: Optional[str] = None) -> bool:
        return bool(self._providers.get(tag, {}).get(provider.name))

    def has_by_metadata(self, metadata: IMetaData, tag: Optional[str] = None) -> bool:
        return bool(self._providers.get(tag, {}).get(metadata.name))

    def merge(self, pool: ProvidersPool) -> ProvidersPool:
        self.set(merge_deep(self.providers, pool.providers))

        return self

    def copy(self) -> ProvidersPool:
        new_pool = ProvidersPool()
        new_pool.set(self._providers)

        return new_pool

    @classmethod
    def from_providers(cls, providers: list[IProvider], tag: Optional[str] = None) -> ProvidersPool:
        new_pool = ProvidersPool()
        for provider in providers:
            new_pool.add(provider, tag)
        return new_pool

    @property
    def providers(self) -> dict[str, dict[str, any]]:
        return self._providers
