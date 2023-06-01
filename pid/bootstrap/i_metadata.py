from typing import Any, Type, TypeVar, Callable, Optional

from ..shared import IProvider


T = TypeVar('T')


class IMetaData:
    class_: Type[T]
    is_module: bool
    imports: list[Any]
    exports: list[Any]
    providers: list[Any]

    name: str

    make_providable: Callable[[Optional[IProvider]], IProvider]

