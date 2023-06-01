from typing import Type, TypeVar, Optional

from .utils import is_injectable, get_metadata
from .const import Mode

from ..shared import IProvider, ClassIsNotInjectable


T = TypeVar('T')


class BootStrap:
    root: dict[str, IProvider] = {}

    @classmethod
    def resolve(cls, class_: Type[T], tag: Optional[str] = None, mode: Mode = Mode.DEV) -> T:
        if cls.root.get(tag) is not None and mode == Mode.DEV:
            return

        if not is_injectable(class_):
            raise ClassIsNotInjectable(class_.__name__)

        metadata = get_metadata(class_)
        providable = metadata.make_providable(None)

        cls.root[tag] = providable

        return providable.resolve(tag=tag)
