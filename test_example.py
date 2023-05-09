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


@Providers.injectable(providers=[Dependency])
class FourthDependency:
    def __init__(self, dependency: Dependency):
        print('FourthDependency', dependency)


@Providers.injectable(providers=[])
class ThirdDependency:
    def __init__(self, dependency: Dependency):
        print('ThirdDependency', dependency)


@Providers.injectable(providers=[ThirdDependency, FourthDependency])
class SecondDependency: ...


@Providers.module(
    imports=[ModuleWithDep],
    providers=[
        SecondDependency,
    ],
)
class RootModule:
    def __init__(self, dependency: Dependency):
        print('RootModule', dependency)


module = BootStrap.resolve(RootModule)
