from __future__ import annotations

from typing import Type, TypeVar, Optional, Any, get_type_hints, get_origin, get_args

from ..bootstrap.utils import get_metadata
from ..pool import DependencyPool, Unknown, ProvidersPool
from ..shared import IProvider, IModule, Dependency, CannotResolveDependency, UndefinedExport, IMetaData


T = TypeVar('T')


class PidModule(IProvider[T]):
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
            get_metadata(import_).make_providable(None) for import_ in imports
        ] if imports else []

        self._exports: list[IMetaData] = [
            get_metadata(export_) for export_ in exports
        ] if exports else []

        self._providers: list[IProvider] = [
            get_metadata(provider_).make_providable(self) for provider_ in providers
        ] if providers else []

        self._pool = DependencyPool()

        self._own_providers_pool = ProvidersPool()
        self._inherit_providers_pool = ProvidersPool()

    def resolve(
        self,
        tag: Optional[str] = None,
    ) -> T:
        resolved_module = self._pool.get(self, tag)

        if resolved_module is not Unknown:
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

        self._own_providers_pool = self._make_own_providers_pool()
        child_providers_pool = self._make_child_providers_pool()

        for provider in self._providers:
            provider.set_providers_pool(child_providers_pool)

        for provider in self._providers:
            self.resolve_child(provider, tag)

        dependencies = self._prepare(tag)
        resolved_module = self._provide(dependencies)

        self._pool.add(self, resolved_module, tag)

        return resolved_module

    def _prepare(self, tag: str) -> dict[str, Any]:
        provider_dependencies = self.dependencies

        dependencies = {}
        for key, dependency in provider_dependencies.items():
            metadata = dependency.metadata

            if not dependency.raw:
                resolved_dependency = self._pool.get_by_meta_data(metadata, tag)

                if resolved_dependency is not Unknown:
                    dependencies[key] = resolved_dependency

                elif self._inherit_providers_pool.has_by_metadata(metadata):
                    related_provider = self._inherit_providers_pool.get_by_metadata(metadata)

                    dependencies[key] = related_provider.owner.resolve_child(related_provider, tag)
                else:
                    raise CannotResolveDependency(f'[{self.name}] {key}')
            else:
                if self._own_providers_pool.has_by_metadata(metadata):
                    dependencies[key] = self._own_providers_pool.get_by_metadata(metadata)
                elif self._inherit_providers_pool.has_by_metadata(metadata):
                    dependencies[key] = self._inherit_providers_pool.get_by_metadata(metadata)
                else:
                    raise CannotResolveDependency(f'[{self.name}] {key}')

        return dependencies

    def _provide(self, dependencies: dict[str, Any]) -> T:
        return self._class(**dependencies)

    def resolve_child(self, provider: IProvider, tag: Optional[str] = None) -> Any:
        resolved_provider = self._pool.get(provider, tag)

        if resolved_provider is not Unknown:
            return resolved_provider

        resolved_provider = provider.resolve(tag)

        self._pool.add(provider, resolved_provider, tag)

        return resolved_provider

    def _make_own_providers_pool(self) -> ProvidersPool:
        pool = ProvidersPool()

        for provider in self._providers:
            pool.add(provider)

        return pool

    def _make_child_providers_pool(self) -> ProvidersPool:
        return self._inherit_providers_pool.copy().merge(self._own_providers_pool)

    def make_export_providers_pool(self) -> ProvidersPool:
        return ProvidersPool.from_providers(self.make_exports())

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

    @property
    def name(self) -> str:
        return self._class.__name__

    @property
    def dependencies(self) -> dict[str, Dependency]:
        method = self._class.__init__

        try:
            init_annotations = get_type_hints(method)
        except AttributeError:
            return {}

        if 'return' in init_annotations:
            del init_annotations['return']

        return {
            key: Dependency(
                metadata=get_metadata(annotation),
                raw=False,
            )

            if not get_origin(annotation) else

            Dependency(
                metadata=get_metadata(get_args(annotation)[0]),
                raw=True,
            )

            for key, annotation
            in init_annotations.items()
        }
