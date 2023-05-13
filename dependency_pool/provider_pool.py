from __future__ import annotations

from collections import defaultdict
from typing import Optional

from shared import IProvider, merge_deep


class ProvidersPool:
    def __init__(self):
        self._providers: dict[str, dict[str, IProvider]] = defaultdict(dict)

    def add(self, provider: IProvider, tag: Optional[str] = None) -> None:
        self._providers[tag][provider.name] = provider

    def get(self, provider: IProvider, tag: Optional[str] = None) -> any:
        return self._providers.get(tag, {}).get(provider.name)

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._providers.clear()
        self._providers.update(dependencies)

    def has_strict(self, provider: IProvider, tag: Optional[str] = None) -> bool:
        return provider is self._providers.get(tag, {}).get(provider.name)

    def with_providers(self, providers: list[IProvider]) -> ProvidersPool:
        requested_provider_names = [provider.name for provider in providers]

        filtered_dependencies = {
            tag: {
                provider_name: provider
                for provider_name, provider
                in provider_pairs.items()
                if provider_name in requested_provider_names
            }
            for tag, provider_pairs
            in self._providers.items()
        }

        new_pool = ProvidersPool()
        new_pool.set(filtered_dependencies)

        return new_pool

    def exclude_providers(self, providers: list[IProvider]) -> ProvidersPool:
        requested_provider_names = [provider.name for provider in providers]

        filtered_dependencies = {
            tag: {
                provider_name: provider
                for provider_name, provider
                in provider_pairs.items()
                if provider_name not in requested_provider_names
            }
            for tag, provider_pairs
            in self._providers.items()
        }

        new_pool = ProvidersPool()
        new_pool.set(filtered_dependencies)

        return new_pool

    def merge(self, pool: ProvidersPool) -> ProvidersPool:
        self.set(merge_deep(self.providers, pool.providers))

        return self

    def copy(self) -> ProvidersPool:
        new_pool = ProvidersPool()
        new_pool.set(self._providers)

        return new_pool

    @property
    def providers(self) -> dict[str, dict[str, any]]:
        return self._providers
