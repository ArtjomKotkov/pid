class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Core(metaclass=Singleton):

    def __init__(self):
        self._dependency_map: dict[str, any] = {}

    def remember(self, dependency: any) -> None:
        dependency_name = dependency._class.__name__

        assert dependency_name not in self._dependency_map, f'Dependency {dependency_name} has duplicate, please rename it.'

        self._dependency_map[dependency_name] = dependency

    def get(self, dependency_name: str) -> any:
        assert dependency_name in self._dependency_map, f'Dependency {dependency_name} doesnt exists globally.'

        return self._dependency_map[dependency_name]
