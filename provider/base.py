from __future__ import annotations

from typing import Callable


class ProvidedUnit:
    name: str
    unresolved_dependencies: dict[str, str]
    tag: str

    provide: Callable
    owner: any
