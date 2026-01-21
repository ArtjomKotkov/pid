from typing import Type

from .utils import is_injectable, get_metadata

from ..shared import ClassIsNotInjectable, ResolveTreeMetadata


class BootStrap:
    @classmethod
    def resolve[T](cls, class_: Type[T]) -> T:
        if not is_injectable(class_):
            raise ClassIsNotInjectable(class_.__name__)

        metadata = get_metadata(class_)
        providable = metadata.make_providable()

        return providable.resolve()
