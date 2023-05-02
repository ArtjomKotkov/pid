from typing import Type, TypeVar, Optional, Self

from provider import Provider
from resolver import ResolveUnit


T = TypeVar('T')


class PidUnit(Provider, ResolveUnit):
    def __init__(
        self,
        class_: Type[T],
        providers: Optional[list[Provider]] = None,
    ):
        super().__init__(class_)

        self._providers = providers or []

    def resolve(self, tag: Optional[str] = None) -> Self:
        return self._resolver.resolve(self)
