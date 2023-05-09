from __future__ import annotations

from collections import defaultdict
from typing import Optional

from .pool_types import UnknownDependency
from shared import AbstractProvider


class DependencyPool:
    def __init__(self):
        self._dependencies: dict[str, dict[str, any]] = defaultdict(dict)

    def add(self, provider: AbstractProvider, resolved_dependency: any, tag: Optional[str] = None) -> None:
        self._dependencies[tag][provider.name] = resolved_dependency

    def get(self, provider: AbstractProvider, tag: Optional[str] = None) -> any:
        return self._dependencies.get(tag, {}).get(provider.name, UnknownDependency)

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._dependencies.clear()
        self._dependencies.update(dependencies)

    def has(self, provider: AbstractProvider, tag: Optional[str] = None) -> bool:
        return provider in self._dependencies.get(tag, {})

    def with_dependencies(self, dependencies: list[AbstractProvider]) -> DependencyPool:
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

    def exclude_dependencies(self, dependencies: list[AbstractProvider]) -> DependencyPool:
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
