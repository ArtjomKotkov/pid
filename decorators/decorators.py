from typing import Type, TypeVar, Optional, Callable, Any

from provider import Provider
from module import PidModule
from bootstrap.const import METADATA_ATTRIBUTE
from bootstrap.metadata import MetaData


ProviderType = Provider | Type
ProvidersType = list[ProviderType]


T = TypeVar('T')


class Providers:
    @staticmethod
    def module(
        *,
        imports: Optional[Any] = None,
        exports: Optional[Any] = None,
        providers: Optional[Any] = None,
    ) -> Callable:
        def wrapper(class_: Type[T]) -> PidModule:

            setattr(
                class_,
                METADATA_ATTRIBUTE,
                MetaData(
                    class_=class_,
                    is_module=True,
                    imports=imports or [],
                    exports=exports or [],
                    providers=providers or [],
                )
            )

            return class_

        return wrapper

    @staticmethod
    def injectable(
        *,
        providers: Optional[Any] = None,
    ) -> Callable:
        def wrapper(class_: Type[T]) -> Provider:
            setattr(
                class_,
                METADATA_ATTRIBUTE,
                MetaData(
                    class_=class_,
                    is_module=False,
                    imports=[],
                    exports=[],
                    providers=providers or [],
                )
            )

            return class_

        return wrapper
