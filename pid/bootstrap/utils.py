from typing import Type, TypeVar

from .const import METADATA_ATTRIBUTE

from ..shared import ClassIsNotInjectable, IMetaData


T = TypeVar('T')


def is_injectable(class_: Type[T]) -> bool:
    return hasattr(class_, METADATA_ATTRIBUTE)


def get_metadata(class_: Type[T]) -> IMetaData:
    if not is_injectable(class_):
        raise ClassIsNotInjectable(class_.__name__)

    return getattr(class_, METADATA_ATTRIBUTE)
