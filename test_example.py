from __future__ import annotations

from decorators import Providers

from bootstrap.bootstrap import BootStrap


@Providers.injectable()
class Dependency: ...


@Providers.module(
    providers=[
        Dependency,
    ],
    exports=[
        Dependency,
    ]
)
class ModuleWithDep:
    def __init__(self, dependency: Dependency):
        print('ModuleWithDep', dependency)


@Providers.injectable()
class SomeDependency:
    # неправильно он получает тут
    def __init__(self, dependency: Dependency):
        print('SomeDependency', dependency)


@Providers.injectable()
class FourthDependency:
    def __init__(self, dependency: Dependency, someDependency: SomeDependency):
        print('FourthDependency', dependency)


@Providers.injectable(providers=[])
class ThirdDependency:
    def __init__(self, dependency: Dependency):
        print('ThirdDependency', dependency)


@Providers.injectable(providers=[ThirdDependency, FourthDependency, Dependency])
class SecondDependency():
    def __init__(self, dependency: Dependency): ...


@Providers.module(
    imports=[ModuleWithDep],
    providers=[
        SecondDependency,
        SomeDependency,
        Dependency,
    ],
)
class RootModule:
    def __init__(self, dependency: Dependency):
        print('RootModule', dependency)


module = BootStrap.resolve(RootModule)