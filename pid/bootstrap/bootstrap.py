from typing import Type, TypeVar

from .utils import is_injectable, get_metadata

from ..shared import ClassIsNotInjectable, ResolveTag


T = TypeVar('T')


class BootStrap:

    @classmethod
    def resolve(cls, class_: Type[T], tag: ResolveTag = None) -> T:
        if not is_injectable(class_):
            raise ClassIsNotInjectable(class_.__name__)

        metadata = get_metadata(class_)
        providable = metadata.make_providable()

        return providable.resolve(tag)
