from __future__ import annotations

from collections import defaultdict
from typing import Optional, Self

from provider import ProvidedUnit


class DependencyPool:
    def __init__(self, shared_dependencies: Optional[list[ProvidedUnit]] = None):
        self._shared_dependencies = shared_dependencies or []

        self._dependencies: dict[str, dict[str, any]] = defaultdict(dict)

    def add(self, name: str, resolved_dependency: any, tag: Optional[str] = None) -> None:
        self._dependencies[tag][name] = resolved_dependency

    def get(self, name: str, tag: Optional[str] = None) -> Optional[any]:
        return self._dependencies.get(tag, {}).get(name)

    def set(self, dependencies: dict[str, dict[str, any]]) -> None:
        self._dependencies = dependencies

    @property
    def shared_dependency_names(self) -> list[str]:
        return [dep.name for dep in self._shared_dependencies]

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
