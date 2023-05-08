from typing import Type, TypeVar, Optional, Callable

from provider import Provider
from module import PidModule


ProviderType = Provider | Type
ProvidersType = list[ProviderType]


T = TypeVar('T')


class Providers:
    @staticmethod
    def module(
        *,
        imports: Optional[ProvidersType] = None,
        exports: Optional[ProvidersType] = None,
        providers: Optional[ProvidersType] = None,
    ) -> Callable:
        def wrapper(class_: Type[T]) -> PidModule:
            return PidModule(
                class_,
                imports,
                exports,
                providers,
            )

        return wrapper

    @staticmethod
    def injectable(
        *,
        providers: Optional[ProvidersType] = None,
    ) -> Callable:
        def wrapper(class_: Type[T]) -> Provider:
            return Provider(
                class_,
                providers,
            )

        return wrapper
