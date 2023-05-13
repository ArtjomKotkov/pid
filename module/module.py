from __future__ import annotations

from typing import Type, TypeVar, Optional, Any, get_type_hints

from bootstrap.utils import get_metadata
from dependency_pool import DependencyPool, UnknownDependency, ProvidersPool
from shared import IProvider
from shared.exceptions import CannotResolveDependency

T = TypeVar('T')


class PidModule(IProvider[T]):
    is_module = True

    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[Any]] = None,
        exports: Optional[list[Any]] = None,
        providers: Optional[list[Any]] = None,
    ) -> None:
        self._class = class_

        self._imports: list[IProvider] = [
            get_metadata(import_).make_providable() for import_ in imports
        ] if imports else []

        self._exports: list[IProvider] = [
            get_metadata(export_).make_providable() for export_ in exports
        ] if exports else []

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable() for provider_ in providers
        ] if providers else []

        self._pool = DependencyPool()
        self._inherit_providers_pool = ProvidersPool()

    @classmethod
    def make_from_class_metadata(cls, class_: Any) -> PidModule:
        metadata = get_metadata(class_)

        return PidModule(
            class_=class_,
            imports=metadata.imports,
            providers=metadata.providers,
            exports=metadata.exports,
        )

    def resolve(
        self,
        tag: Optional[str] = None,
    ) -> T:
        resolved_module = self._pool.get(self, tag)

        if resolved_module is not UnknownDependency:
            return resolved_module

        try:
            return self._resolve(tag)
        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        tag: Optional[str] = None,
    ) -> T:
        for module in self._imports:
            module.resolve(tag)
            export_pool = module.make_export_providers_pool()

            self._inherit_providers_pool.merge(export_pool)

        for provider in self._providers:
            self.resolve_child(provider, tag)

        return self._provide(tag)

    def _provide(self, tag:  Optional[str] = None) -> T:
        dependencies = {
            key: self._pool.get(dependency, tag)
            for key, dependency
            in self.dependencies.items()
        }

        unknown_dependencies = [
            (key, self.dependencies[key],)
            for key, dep
            in dependencies.items()
            if dep is UnknownDependency
        ]

        if unknown_dependencies:
            dep_string = '\n'.join([f'{self.name}: {dep_pair[0]} - {dep_pair[1]}' for dep_pair in unknown_dependencies])
            error_msg = '\nCurrent dependencies isn\'t provided in any bounded module.\n' + dep_string

            raise CannotResolveDependency(error_msg)

        provided_module = self._class(**dependencies)
        self._pool.add(self, provided_module, tag)

        return provided_module

    def resolve_child(self, provider: IProvider, tag: Optional[str] = None) -> Any:
        own_providers_pool = self._make_own_providers_pool(tag)
        child_providers_pool = self._inherit_providers_pool.copy().merge(own_providers_pool)

        if not child_providers_pool.has_strict(provider, tag):
            raise CannotResolveDependency()

        resolved_provider = self._pool.get(provider, tag)

        if resolved_provider is not UnknownDependency:
            return resolved_provider

        resolved_provider = provider.resolve(
            child_providers_pool,
            tag,
        )

        self._pool.add(provider, resolved_provider, tag)

        return resolved_provider

    def _make_own_providers_pool(self, tag: Optional[str] = None) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider, tag)

        return pool

    def make_export_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.with_providers(self._make_exports())

    def _make_exports(self) -> list[IProvider]:
        export_providers = []

        for export_unit in self._exports:
            if export_unit.is_module:
                export_providers.extend(export_unit._make_exports())
            else:
                export_providers.append(export_unit)

        return export_providers

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def providers(self) -> list[IProvider]:
        return self._providers

    @property
    def dependencies(self) -> dict[str, IProvider]:
        method = self._class.__init__

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: get_metadata(class_).make_providable()
            for key, class_
            in init_annotations.items()
        }
