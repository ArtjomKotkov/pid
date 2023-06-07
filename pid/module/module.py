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
        self._class = class_

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
        available_providers_for_export = self._make_child_providers_pool().get_all()

        providers_names_to_export = []

        for export_unit in self._exports:
            if export_unit.is_module:
                export_module = next(module for module in self._imports if module.name == export_unit.name)
                providers_names_to_export.extend([provider.name for provider in export_module.make_exports()])
            else:
                providers_names_to_export.append(export_unit.name)

        undefined_exports = [
            name
            for name in providers_names_to_export
            if name not in available_providers_for_export
        ]

        if undefined_exports:
            raise UndefinedExport()

        return [provider for name, provider in available_providers_for_export.items() if name in providers_names_to_export]

    def _make_own_providers_pool(self) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider)

        return pool

    def _make_child_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.copy().merge(self._own_providers_pool)

    @property
    def provider_method(self) -> Callable[[*Any], T]:
        return self._class.__init__
