from __future__ import annotations

from typing import Type, TypeVar, Optional

from dependency_pool import DependencyPool, UnknownDependency
from shared import AbstractProvider
from shared.exceptions import CannotResolveDependency
from provider import Provider

T = TypeVar('T')


class PidModule(AbstractProvider[T]):
    is_module = True

    def __init__(
        self,
        class_: Type[T],
        imports: Optional[list[PidModule]] = None,
        exports: Optional[list[Provider]] = None,
        providers: Optional[list[Provider]] = None,
    ) -> None:
        self._class = class_

        self._imports = imports or []
        self._exports = exports or []
        self._providers = providers or []

        self._pool = DependencyPool()

    def resolve(
        self,
        inherit_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        resolved_module = self._pool.get(self, tag)

        if resolved_module is not UnknownDependency:
            inherit_pool.merge(self._pool.with_dependencies(self._exports))
            return resolved_module

        try:
            for module in self._imports:
                node_pool = DependencyPool()

                module.resolve(node_pool, tag)

                self._pool.merge(node_pool)

            if not inherit_pool:
                inherit_pool = DependencyPool()

            return self._resolve(inherit_pool, tag)

        except RecursionError:
            raise RecursionError('Recursion error means, that you are trying to resolve some dependencies manualy in class initializer. It\'s not allowed at the moment.\nPlease resolve your dependencies manually in class methods.')

    def _resolve(
        self,
        inherit_pool: Optional[DependencyPool] = None,
        tag: Optional[str] = None,
    ) -> T:
        for provider in self._providers:
            resolved_provider = provider.resolve(
                self._pool.exclude_dependencies(self._providers),
                self._providers,
                tag,
            )
            self._pool.add(provider, resolved_provider, tag)

        inherit_pool.merge(self._pool.with_dependencies(self._make_exports()))

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

    def _make_exports(self) -> list[Provider]:
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
    def providers(self) -> list[Provider]:
        return self._providers
