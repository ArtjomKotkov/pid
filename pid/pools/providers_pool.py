from __future__ import annotations

from typing import Any, Type, Optional

from ..shared import IProvider, merge_deep, MultipleProvidersForAlias


class ProvidersPool:
    def __init__(self):
        self._providers: dict[tuple[type, Any], IProvider] = {}

    def add(self, provider: IProvider) -> None:
        aliases = self._get_class_aliases(provider.class_)

        self._providers[aliases] = provider

    def get(self, class_: Type[Any]) -> Any:
        result: Optional[IProvider] = None

        for aliases_record, provider in self._providers.items():
            aliases_record_set = set(aliases_record)

            if {class_}.intersection(aliases_record_set):
                if result is None:
                    result = provider
                else:
                    raise MultipleProvidersForAlias()

        return result

    def get_all(self) -> dict[tuple[type, Any], IProvider]:
        return self._providers

    def has(self, class_: Type[Any]) -> bool:
        return bool(self.get(class_))

    def merge(self, pool: ProvidersPool) -> ProvidersPool:
        self._set(merge_deep(self._providers, pool._providers))

        return self

    def copy(self) -> ProvidersPool:
        new_pool = ProvidersPool()
        new_pool._set(self._providers)

        return new_pool

    @classmethod
    def from_providers(cls, providers: list[IProvider]) -> ProvidersPool:
        new_pool = ProvidersPool()
        for provider in providers:
            new_pool.add(provider)
        return new_pool

    @staticmethod
    def _get_class_aliases(class_: Type[Any]) -> tuple[type, Any]:
        return (class_, *(class_.__orig_bases__ if hasattr(class_, '__orig_bases__') else class_.__bases__))

    def _set(self, dependencies: dict[tuple[type, Any], IProvider]) -> None:
        self._providers.clear()
        self._providers.update(dependencies)
