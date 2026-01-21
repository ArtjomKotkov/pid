from __future__ import annotations

from copy import copy
from typing import Type, Optional, Any, Callable

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import (
    IProvider, IModule,
    UndefinedExport, IMetaData,
    ResolveTreeMetadata,
)
from ..abstract import AbstractProvider


class PidModule[T](AbstractProvider[T]):
    is_module = True

    __instances__ = {}

    def __new__(
        cls,
        class_: Type[T],
        imports: Optional[list[Any]] = None,
        exports: Optional[list[Any]] = None,
        providers: Optional[list[Any]] = None,
    ):
        return cls._get_or_create_instance(class_)

    @classmethod
    def _get_or_create_instance(cls, class_: Type[T]) -> 'PidModule':
        instance = cls.__instances__.get(class_.__name__)
        if instance is None:
            cls.__instances__[class_.__name__] = super().__new__(cls)
        return cls.__instances__.get(class_.__name__)

    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[Any]] = None,
        exports: Optional[list[Any]] = None,
        providers: Optional[list[Any]] = None,
    ) -> None:
        self.class_ = class_
        self._imports = self._initialize_imports(imports)
        self._exports = self._initialize_exports(exports)
        self._providers = self._initialize_providers(providers)
        self._initialize_pools()

    def _initialize_imports(self, imports: Optional[list[Any]]) -> list[IModule]:
        return [get_metadata(import_).make_providable() for import_ in imports] if imports else []

    def _initialize_exports(self, exports: Optional[list[Any]]) -> list[IMetaData]:
        return [get_metadata(export_) for export_ in exports] if exports else []

    def _initialize_providers(self, providers: Optional[list[Any]]) -> list[IProvider]:
        return [get_metadata(provider_).make_providable() for provider_ in providers] if providers else []

    def _initialize_pools(self) -> None:
        self._resolved_module = None
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def resolve(
        self,
        resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> T:
        resolve_tree_metadata = resolve_tree_metadata or ResolveTreeMetadata([])

        return self._resolve(resolve_tree_metadata)

    def _resolve(
        self,
        resolve_tree_metadata: ResolveTreeMetadata = None,
    ) -> T:
        resolve_tree_metadata.chain.append(self.class_.__name__)

        if self._resolved_module:
            return self._resolved_module

        self._resolve_imports(resolve_tree_metadata)
        self._update_provider_pools()
        resolved_module = self._provide(resolve_tree_metadata)
        self._resolved_module = resolved_module

        return self._resolved_module

    def _resolve_imports(self, resolve_tree_metadata: ResolveTreeMetadata) -> None:
        for module in self._imports:
            module.resolve(copy(resolve_tree_metadata))
            export_pool = ProvidersPool.from_providers(module.make_exports())
            self._inherit_providers_pool.merge(export_pool)

    def _update_provider_pools(self) -> None:
        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()
        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

    def make_exports(self) -> list[IProvider]:
        child_providers_pool = self._make_child_providers_pool()

        export_units_metadata_for_export = []

        for export_unit_metadata in self._exports:
            if export_unit_metadata.is_module:
                export_module = next(module for module in self._imports if module.class_ is export_unit_metadata.class_)
                export_units_metadata_for_export.extend([provider for provider in export_module.make_exports()])
            else:
                export_units_metadata_for_export.append(export_unit_metadata)

        undefined_exports = [
            metadata
            for metadata in export_units_metadata_for_export
            if not child_providers_pool.has(metadata.class_)
        ]

        if undefined_exports:
            raise UndefinedExport()

        return [child_providers_pool.get(metadata.class_) for metadata in export_units_metadata_for_export]

    def _make_own_providers_pool(self) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider)

        return pool

    def _make_child_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.copy().merge(self._own_providers_pool)

    @property
    def provider_method(self) -> Callable[[*Any], T]:
        return self.class_.__init__
