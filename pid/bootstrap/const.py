from enum import StrEnum


__all__ = [
    'METADATA_ATTRIBUTE',
    'Mode'
]


METADATA_ATTRIBUTE = '_pid_metadata_'


class Mode(StrEnum):
    TEST = 'test'
    DEV = 'DEV'
