
from typing import Any, Optional

from core import Core
from exceptions import CannotResolveDependency
from provider import ProvidedUnit
from dependency_pool import DependencyPool, SharedDependencyPool


class DependencyResolver:
    def __init__(
        self,
        pool: DependencyPool,
        shared_pool: SharedDependencyPool,
    ):
        self._pool = pool
        self._shared_pool = shared_pool

        self._core = Core()

    def resolve(
        self,
        dependency: ProvidedUnit,
        available_providers: Optional[list[ProvidedUnit]] = None,
        own_providers: Optional[list[ProvidedUnit]] = None,
        parent: Optional[ProvidedUnit] = None,
        tag: Optional[str] = None,
    ) -> Any:
        self_resolved_dep = self._pool.get(dependency.name, tag)
        inherited_resolved_dep = self._shared_pool.get(dependency.name, tag)

        if self_resolved_dep:
            return self_resolved_dep

        if inherited_resolved_dep and dependency not in own_providers:
            return inherited_resolved_dep

        # if available_providers is not None:
        #     errors = self._can_resolve(dependency, available_providers, parent)
        #     if errors is not None:
        #         error_string = '\nCurrent dependencies isn\'t provided in any bounded module.\n' + '\n'.join(' '.join(paths) for paths in errors)
        #         raise CannotResolveDependency(error_string)

        unresolved_inner_deps = dependency.dependencies

        if not all(
            (
                self._core.get(dep_name).dependency in available_providers
                or self._shared_pool.has(dep_name, tag)
            )
            for dep_name
            in unresolved_inner_deps.values()
        ):
            raise ValueError('INVALID')

        resolved_inner_dependencies = {}
        for key, dep_name in unresolved_inner_deps.items():
            core_unit = self._core.get(dep_name)

            resolved_inner_dependencies[key] = (
                self.resolve(
                    core_unit.dependency,
                    available_providers,
                    own_providers=own_providers,
                    tag=tag,
                )
                if not core_unit.request_unresolved
                else core_unit.dependency
            )

        provided_dependency = dependency.provide(resolved_inner_dependencies)
        self._pool.add(dependency.name, provided_dependency, tag)
        return provided_dependency

    def _can_resolve(
        self,
        dependency: ProvidedUnit,
        available_providers: list[ProvidedUnit],
        parent: Optional[ProvidedUnit] = None,
    ) -> list[list[str]]:
        errors = []

        parent_name = parent.name if parent else '-'

        unresolved_inner_deps = {
            self._core.get(dep_name).dependency
            for dep_name
            in dependency.unresolved_dependencies.values()
        }

        self_unrecognized_deps = unresolved_inner_deps.difference(available_providers)

        errors.extend([[parent_name, dependency.name, dep.name] for dep in self_unrecognized_deps])

        child_unrecognized_deps_errors = [
            self._can_resolve(inner_dep, available_providers, dependency)
            for inner_dep
            in unresolved_inner_deps
        ]

        for child_errors in child_unrecognized_deps_errors:
            if child_errors:
                errors.extend([
                    [parent_name, *child_unrecognized_deps_error]
                    for child_unrecognized_deps_error
                    in child_errors
                    if child_unrecognized_deps_error
                ])

        return errors if errors else None

    @property
    def pool(self) -> DependencyPool:
        return self._pool
