__all__ = [
    'CannotResolveDependency',
    'UndefinedExport',
    'ClassIsNotInjectable',
    'MultipleProvidersForAlias',
]


class CannotResolveDependency(Exception): ...


class UndefinedExport(Exception): ...


class ClassIsNotInjectable(Exception): ...


class MultipleProvidersForAlias(Exception): ...
