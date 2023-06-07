from typing import Type, TypeVar, Optional, Callable, Any

from ..bootstrap.const import METADATA_ATTRIBUTE
from ..bootstrap.metadata import MetaData


T = TypeVar('T')


class Pid:
    @staticmethod
    def module(
        *,
        imports: Optional[Any] = None,
        exports: Optional[Any] = None,
        providers: Optional[Any] = None,
    ) -> Callable:
        def wrapper(class_: Type[T]) -> Type[T]:

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
        factory: Optional[Callable[[Any], T]] = None
    ) -> Callable:
        def wrapper(class_: Type[T]) -> Type[T]:
            setattr(
                class_,
                METADATA_ATTRIBUTE,
                MetaData(
                    class_=class_,
                    is_module=False,
                    imports=[],
                    exports=[],
                    providers=providers or [],
                    factory=factory,
                )
            )

            return class_

        return wrapper
