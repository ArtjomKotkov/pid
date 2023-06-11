from typing import Any, Hashable


DictOfDicts = dict[Hashable, dict[str, Any] | Any]


__all__ = [
    'merge_deep'
]


def merge_deep(dict1: DictOfDicts, dict2: DictOfDicts) -> DictOfDicts:
    all_keys = {*list(dict1.keys()), *list(dict2.keys())}

    result = {}

    for key in all_keys:
        value1 = dict1.get(key, {})
        value2 = dict2.get(key, {})

        if isinstance(value1, dict) and isinstance(value2, dict):
            result[key] = merge_deep(value1, value2)
        else:
            result[key] = value2 or value1

    return result
