from typing import Any, Optional

from core import Core
from exceptions import CannotResolveDependency
from provider import Provider


class DependencyResolver:
    def __init__(self):
        self._core = Core()

        self._dependencies: dict[str, any] = {}

    def resolve(
        self,
        dependency: Provider,
        available_providers: list[Provider],
        parent: Optional[Provider] = None,
        is_module: bool = False,
    ) -> Any:

        errors = self._can_resolve(dependency, available_providers, parent)
        if errors is not None:
            error_string = '\nCurrent dependencies isn\'t provided in any bounded module.\n' + '\n'.join(' '.join(paths) for paths in errors)
            raise CannotResolveDependency(error_string)

        if self._dependencies.get(dependency.name):
            return self._dependencies[dependency.name]

        unresolved_inner_deps = dependency.unresolved_dependencies

        resolved_inner_dependencies = {
            key: self.resolve(self._core.get(dep_name), available_providers)
            for key, dep_name
            in unresolved_inner_deps.items()
        }

        if not is_module:
            self._dependencies[dependency.name] = dependency.provide(resolved_inner_dependencies)
            return self._dependencies[dependency.name]
        else:
            return dependency.provide(resolved_inner_dependencies)

    def _can_resolve(
        self,
        dependency: Provider,
        available_providers: list[Provider],
        parent: Optional[Provider] = None,
    ) -> list[list[str]]:
        errors = []

        parent_name = parent.name if parent else '-'

        unresolved_inner_deps = {
            self._core.get(dep_name)
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
