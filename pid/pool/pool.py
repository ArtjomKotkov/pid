from __future__ import annotations

from collections import defaultdict
from typing import Optional, Any

from .pool_types import Unknown

from ..shared import IProvider, IMetaData, PidTag


class DependencyPool:
    def __init__(self):
        self._dependencies: dict[str, dict[str, Any]] = defaultdict(dict)

    def add(self, provider: IProvider, resolved_dependency: Any, tag: Optional[str] = None) -> None:
        self._dependencies[tag][provider.name] = resolved_dependency

    def get(self, provider: IProvider, tag: Optional[str] = None) -> Any:
        name = provider.name

        default_value = self._find_in_defaults(name, tag)
        if default_value is not Unknown:
            return default_value

        return self._dependencies.get(tag, {}).get(name, Unknown)

    def get_by_meta_data(self, meta_provider: IMetaData, tag: Optional[str] = None) -> Any:
        name = meta_provider.class_.__name__

        default_value = self._find_in_defaults(name, tag)
        if default_value is not Unknown:
            return default_value

        return self._dependencies.get(tag, {}).get(name, Unknown)

    def _find_in_defaults(self, name: str, tag: Optional[str] = None) -> Any:
        default_values = {
            PidTag.__name__: tag,
        }

        return default_values.get(name, Unknown)
