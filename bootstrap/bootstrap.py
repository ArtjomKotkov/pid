from typing import Type, TypeVar, Optional

from shared import IProvider

from .exceptions import ClassIsNotInjectable
from .utils import is_injectable, get_metadata

T = TypeVar('T')


class BootStrap:
    root: dict[str, IProvider] = {}

    @classmethod
    def resolve(cls, class_: Type[T], tag: Optional[str] = None) -> T:
        if cls.root.get(tag) is not None:
            return

        if not is_injectable(class_):
            raise ClassIsNotInjectable(class_.__name__)

        metadata = get_metadata(class_)
        providable = metadata.make_providable()

        cls.root[tag] = providable

        return providable.resolve(tag=tag)
