from typing import Type, TypeVar, Optional

from pid_types import ProvidersType
from provider import Provider


T = TypeVar('T')


class PidUnit(Provider):
    def __init__(
        self,
        class_: Type[T],
        providers: Optional[ProvidersType] = None,
    ):
        super().__init__(class_)

        self._providers = providers or []
