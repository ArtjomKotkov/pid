__all__ = [
    'CannotResolveDependency',
    'UndefinedExport',
    'ClassIsNotInjectable'
]


class CannotResolveDependency(Exception): ...


class UndefinedExport(Exception): ...


class ClassIsNotInjectable(Exception): ...
