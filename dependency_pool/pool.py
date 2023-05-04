from __future__ import annotations

from collections import defaultdict
from typing import Optional, Self

from .pool_types import UnknownDependency
from provider import ProvidedUnit


class DependencyPool:
    def __init__(self):
        self._dependencies: dict[str, dict[str, any]] = defaultdict(dict)

    def add(self, name: str, resolved_dependency: any, tag: Optional[str] = None) -> None:
        self._dependencies[tag][name] = resolved_dependency

    def get(self, name: str, tag: Optional[str] = None) -> any:
        return self._dependencies.get(tag, {}).get(name, UnknownDependency())

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._dependencies.clear()
        self._dependencies.update(dependencies)

    def has(self, name: str, tag: Optional[str] = None) -> bool:
        return name in self._dependencies.get(tag, {})

    def with_dependencies(self, dependencies: list[ProvidedUnit]) -> DependencyPool:
        requested_dependency_names = [dep.name for dep in dependencies]

        filtered_dependencies = {
            tag: {
                name: dependency
                for name, dependency
                in dependency_pairs.items()
                if name in requested_dependency_names
            }
            for tag, dependency_pairs
            in self._dependencies.items()
        }

        new_pool = DependencyPool()
        new_pool.set(filtered_dependencies)

        return new_pool

    def with_dependencies_update(self, dependencies: list[ProvidedUnit]) -> DependencyPool:
        requested_dependency_names = [dep.name for dep in dependencies]

        filtered_dependencies = {
            tag: {
                name: dependency
                for name, dependency
                in dependency_pairs.items()
                if name in requested_dependency_names
            }
            for tag, dependency_pairs
            in self._dependencies.items()
        }

        self.set(filtered_dependencies)

        return self

    def exclude_dependencies(self, dependencies: list[ProvidedUnit]) -> DependencyPool:
        requested_dependency_names = [dep.name for dep in dependencies]

        filtered_dependencies = {
            tag: {
                name: dependency
                for name, dependency
                in dependency_pairs.items()
                if name not in requested_dependency_names
            }
            for tag, dependency_pairs
            in self._dependencies.items()
        }

        new_pool = DependencyPool()
        new_pool.set(filtered_dependencies)

        return new_pool

    def merge(self, pool: DependencyPool) -> DependencyPool:
        merged_deps = {}

        for tag, values in pool.dependencies.items():
            merged_deps[tag] = {
                **self._dependencies[tag],
                **values,
            }

        self.set(merged_deps)

        return self

    @property
    def dependencies(self) -> dict[str, dict[str, any]]:
        return self._dependencies


class SharedDependencyPool:
    def __init__(
        self
    ) -> None:
        self._dependencies: dict[str, dict[str, any]] = defaultdict(dict)

    def get(self, name: str, tag: Optional[str] = None) -> Optional[any]:
        return self._dependencies.get(tag, {}).get(name)

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._dependencies = dependencies

    def has(self, name: str, tag: Optional[str] = None) -> bool:
        return name in self._dependencies.get(tag, {})

    def fill_from_main_pool(self, pool: DependencyPool) -> Self:
        deps_to_update = self._dependencies

        for tag, values in pool.dependencies.items():
            deps_to_update[tag] = {
                **deps_to_update[tag],
                **{
                    name: dep
                    for name, dep
                    in values.items()
                    if name in pool.shared_dependency_names
                },
            }

        self.set(deps_to_update)

        return self

    def merge(self, pool: SharedDependencyPool) -> SharedDependencyPool:
        deps_to_update = self._dependencies

        for tag, values in pool.dependencies.items():
            deps_to_update[tag] = {
                **deps_to_update[tag],
                **values,
            }

        self.set(deps_to_update)

        return self

    @property
    def dependencies(self) -> dict[str, dict[str, any]]:
        return self._dependencies
