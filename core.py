import re
from collections import defaultdict
from typing import NamedTuple, Optional

from provider import ProvidedUnit


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CoreUnit(NamedTuple):
    dependency: ProvidedUnit
    request_unresolved: bool


class Core(metaclass=Singleton):

    def __init__(self):
        self._dependency_map: dict[str, ProvidedUnit] = {}

    def remember_dependency(self, dependency: ProvidedUnit) -> None:
        dependency_name = dependency.name

        assert dependency_name not in self._dependency_map, f'Dependency {dependency_name} has duplicate, please rename it.'

        self._dependency_map[dependency_name] = dependency

    def get(
        self,
        dependency_name: str,
    ) -> CoreUnit:
        provider_regex = re.compile(r'^Provider\[([a-zA-Z]+)]$')

        if match := provider_regex.match(dependency_name):
            dep_name = match.group(1)
            assert dep_name in self._dependency_map, f'Dependency {dep_name} doesnt exists globally.'
            return CoreUnit(dependency=self._dependency_map[dep_name], request_unresolved=True)

        assert dependency_name in self._dependency_map, f'Dependency {dependency_name} doesnt exists globally.'

        return CoreUnit(dependency=self._dependency_map[dependency_name], request_unresolved=False)
