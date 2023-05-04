from __future__ import annotations

from decorators import Providers
from provider import Provider, ProviderWrapper



@Providers.injectable()
class SecondDep:
    a = 12


@Providers.module(
    providers=[
        SecondDep,
    ],
    exports=[
        SecondDep,
    ]
)
class SecondModule:
    def __init__(self, secondDep: SecondDep):
        secondDep.a = 13
        print(secondDep.a)


@Providers.injectable()
class SomeDep:
    a = 12


@Providers.module(
    imports=[SecondModule],
    providers=[
        SomeDep,
        SecondDep,
    ]
)
class RootModule:
    def __init__(self, some: SomeDep, second: SecondDep):
        print(second.a)


module = RootModule.resolve()

a = 12