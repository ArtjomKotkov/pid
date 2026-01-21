from typing import Any, Type, Optional, Callable

from ..module import PidModule
from ..provider import Provider
from ..shared import IProvider, IMetaData


class MetaData[T](IMetaData[T]):
    def __init__(
        self,
        class_: Type[T],
        is_module: bool,
        imports: list[Any] = None,
        exports: list[Any] = None,
        providers: list[Any] = None,
        factory: Optional[Callable[[*Type[Provider]], T]] = None
    ):
        self.class_ = class_
        self.is_module = is_module
        self.imports = imports
        self.exports = exports
        self.providers = providers
        self.factory = factory

    @property
    def name(self) -> str:
        return self.class_.__name__

    def make_providable(self) -> IProvider:
        if self.is_module:
            return PidModule(
                class_=self.class_,
                imports=self.imports,
                providers=self.providers,
                exports=self.exports,
            )
        else:
            return Provider(
                class_=self.class_,
                providers=self.providers,
                factory=self.factory,
            )
