from __future__ import annotations

from collections import defaultdict
from typing import Optional

from .pool_types import Unknown

from ..bootstrap.i_metadata import IMetaData
from ..shared import IProvider


class DependencyPool:
    def __init__(self):
        self._dependencies: dict[str, dict[str, any]] = defaultdict(dict)

    def add(self, provider: IProvider, resolved_dependency: any, tag: Optional[str] = None) -> None:
        self._dependencies[tag][provider.name] = resolved_dependency

    def get(self, provider: IProvider, tag: Optional[str] = None) -> any:
        return self._dependencies.get(tag, {}).get(provider.name, Unknown)

    def get_by_meta_data(self, meta_provider: IMetaData, tag: Optional[str] = None) -> any:
        return self._dependencies.get(tag, {}).get(meta_provider.class_.__name__, Unknown)
