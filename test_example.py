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
        print(dependency)



@Providers.injectable()
class ThirdDependency:
    def __init__(self, dependency: Dependency):
        print(dependency)


@Providers.injectable(providers=[ThirdDependency, Dependency])
class SecondDependency: ...


@Providers.module(
    imports=[ModuleWithDep],
    providers=[
        SecondDependency,
    ],
)
class RootModule:
    def __init__(self, dependency: Dependency):
        print(dependency)


module = BootStrap.resolve(RootModule)
