from typing import Type, TypeVar, Optional

from .utils import is_injectable, get_metadata

from ..shared import ClassIsNotInjectable


T = TypeVar('T')


class BootStrap:

    @classmethod
    def resolve(cls, class_: Type[T], tag: Optional[str] = None) -> T:
        if not is_injectable(class_):
            raise ClassIsNotInjectable(class_.__name__)

        metadata = get_metadata(class_)
        providable = metadata.make_providable(None)

        return providable.resolve(tag)
