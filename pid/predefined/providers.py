from ..shared import PidTag
from ..decorators import Pid


__all__ = [
    'Tag',
]


Tag = Pid.injectable()(PidTag)
