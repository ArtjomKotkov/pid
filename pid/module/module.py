from __future__ import annotations

from typing import Type, TypeVar, Optional, Any, Callable

from ..bootstrap.utils import get_metadata
from ..pools import Unknown, ProvidersPool, ResolvePool
from ..shared import (
    IProvider, IModule,
    UndefinedExport, IMetaData,
    ResolveTag,
)
from ..abstract import AbstractProvider


T = TypeVar('T')


class PidModule(AbstractProvider[T]):
    is_module = True

    __instances__ = {}

    def __new__(
        cls,
        class_: Type[T],
        imports: Optional[list[Any]] = None,
        exports: Optional[list[Any]] = None,
        providers: Optional[list[Any]] = None,
    ):
        instance = cls.__instances__.get(class_.__name__)

        if instance is None:
            cls.__instances__[class_.__name__] = super().__new__(
                cls,
            )

        return cls.__instances__.get(class_.__name__)

    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[Any]] = None,
        exports: Optional[list[Any]] = None,
        providers: Optional[list[Any]] = None,
    ) -> None:
        self.class_ = class_

        self._imports: list[IModule] = [
            get_metadata(import_).make_providable() for import_ in imports
        ] if imports else []

        self._exports: list[IMetaData] = [
            get_metadata(export_) for export_ in exports
        ] if exports else []

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable() for provider_ in providers
        ] if providers else []

        self._resolve_pool = ResolvePool()
        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def resolve(
        self,
        tag: ResolveTag = None,
    ) -> T:
        return self._resolve(tag)

    def _resolve(
        self,
        tag: ResolveTag = None,
    ) -> T:
        resolved_module = self._resolve_pool.get(tag)

        if resolved_module is not Unknown:
            return resolved_module

        for module in self._imports:
            module.resolve(tag)
            export_pool = ProvidersPool.from_providers(module.make_exports())

            self._inherit_providers_pool.merge(export_pool)

        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

        resolved_module = self._provide(tag)

        self._resolve_pool.add(resolved_module, tag)

        return resolved_module

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
